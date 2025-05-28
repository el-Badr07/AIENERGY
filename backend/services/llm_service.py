import os
import logging
from typing import List, Dict, Any, Optional
import groq
from flask import current_app
import dotenv 
from utils.file_utils import extract_json_from_response

dotenv.load_dotenv(override=True)

logger = logging.getLogger(__name__)

class LLMService:
    """Service for analyzing invoice data using Groq LLM"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM service with Groq
        
        Args:
            api_key: Groq API key (defaults to environment variable)
            model: Groq model to use (defaults to environment variable or 'llama3-70b-8192')
        """
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            logger.warning("No Groq API key provided. LLM functionality will be limited.")
        
        self.model = model or os.environ.get('GROQ_MODEL', 'llama3-70b-8192')
        self.client = groq.Client(api_key=self.api_key) if self.api_key else None
    
    def extract_invoice_data(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract structured data from OCR text using LLM
        
        Args:
            ocr_text: Raw text extracted from the invoice
            
        Returns:
            Structured invoice data
        """
        if not self.client:
            logger.error("Groq client not initialized. Cannot extract invoice data.")
            raise ValueError("Groq client not initialized")
        
        prompt_old = f"""
        You are an AI assistant specialized in extracting information from energy invoices.
        Extract the following information from this energy invoice text:
        
        1. Provider name
        2. Invoice number
        3. Issue date (in YYYY-MM-DD format)
        4. Due date (in YYYY-MM-DD format)
        5. Customer name
        6. Customer ID
        7. Total amount
        8. Energy consumption period (start and end dates)
        9. Total kWh consumed
        10. Rate per kWh
        11. Peak kWh (if available)
        12. Off-peak kWh (if available)
        13. Line items with descriptions, quantities, unit prices, and totals
        14. Taxes (with names and amounts)
        
        Return the information in a structured JSON format with these exact keys:
        provider, invoice_number, issue_date, due_date, customer_name, customer_id, 
        total_amount, period_start, period_end, total_kwh, rate_per_kwh, peak_kwh, 
        off_peak_kwh, items (array of objects), taxes (object with tax names as keys and amounts as values)
        
        Here is the invoice text:
        {ocr_text}
        return just a json , no text no remarks no ```json just the json
        """

        prompt = f"""
                    Vous êtes un assistant IA spécialisé dans l'extraction d'informations à partir de factures d'énergie.
            Le texte de la facture fourni est en français.
            Extrayez les informations suivantes de ce texte de facture d'énergie :

            1.  **Nom du fournisseur**: Identifiez le nom de l'entreprise de services publics (par exemple, "LYDEC").
            2.  **Numéro de facture**: Recherchez "N° FACTURE" ou "Détail de votre facture N°" suivi d'un numéro.
            3.  **Date d'émission**: Trouvez "Date de l'édition" et formatez-la au format AAAA-MM-JJ.
            4.  **Date d'échéance**: Si elle est explicitement indiquée (par exemple, "Date limite de paiement"), formatez-la au format AAAA-MM-JJ. Si non trouvée, retournez `null`.
            5.  **Nom du client**: Si disponible, extrayez le nom complet du client. Si non trouvé, retournez `null`.
            6.  **ID client**: Si disponible, extrayez le numéro d'identification du client. Si non trouvé, retournez `null`.
            7.  **Montant total**: Trouvez le "Montant TTC" ou "Total général" (Total toutes taxes comprises).
            8.  **Période de consommation d'énergie**: Déterminez les dates de début et de fin de la période de consommation. Celles-ci sont généralement indiquées par la date de "Ancien Index" (début) et la date de "Nouvel Index" (fin) sous la section "Détail de votre consommation". Formatez les deux au format AAAA-MM-JJ.
            9.  **Total kWh consommés**: Recherchez "Total énergie Active" ou la somme des catégories de consommation (par exemple, "Heures Normales", "Heures Creuses", "Heures de Pointe").
            10. **Tarif par kWh**: Ce tarif peut varier selon la catégorie de consommation ; si un tarif global unique n'est pas disponible, retournez `null`. Le prompt extraira les tarifs individuels dans les postes.
            11. **kWh Pointe**: Extrayez la valeur de consommation pour les "Heures de Pointe". Si "Heures de Pointe" n'est pas présente mais "Heures Normales" l'est, considérez "Heures Normales" comme la pointe.
            12. **kWh Creuses**: Extrayez la valeur de consommation pour les "Heures Creuses".
            13. **Postes détaillés (Line items)**: Extrayez les détails du tableau principal de consommation/services (par exemple, sous "DISTRIBUTION MT"). Pour chaque poste, capturez :
                *   `description`: Le nom de la charge ou du service (par exemple, "CONSO. H. NORMALES", "RDV. DE PUISSANCE").
                *   `quantity`: La valeur sous la colonne "Quantité".
                *   `unit_price`: La valeur sous la colonne "Prix Unitaire H.T.".
                *   `total`: La valeur sous la colonne "Montant H.T.".
            14. **Taxes**: Extrayez les détails des taxes de la section "Récapitulatif TVA". Créez un objet où les clés sont les noms des taxes (par exemple, "TVA_7_percent", "TVA_14_percent" basés sur la colonne "Taux") et les valeurs sont leurs "Montant" correspondants.

            Retournez les informations dans un format JSON structuré avec ces clés exactes :
            `provider`, `invoice_number`, `issue_date`, `due_date`, `customer_name`, `customer_id`,
            `total_amount`, `period_start`, `period_end`, `total_kwh`, `rate_per_kwh`, `peak_kwh`,
            `off_peak_kwh`, `items` (tableau d'objets tel que décrit ci-dessus), `taxes` (objet avec les noms de taxes comme clés et les montants comme valeurs).
            Si un champ n'est pas trouvé, retournez `null` pour ce champ spécifique.

            Voici le texte de la facture :
            {ocr_text}
            retournez juste un json, sans texte, sans remarques, sans ```json juste le json
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that extracts structured data from energy invoices.you return just a valid json, do not put ```json in first or at the end of the response , just put the json"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                # max_tokens=1000
            )
            # print('first response',response)
            # Extract and parse the JSON response
            result = response.choices[0].message.content
            result = extract_json_from_response(result)
            print('result after extract',result)
            
            # In a real implementation, you would parse the JSON string
            # and validate it against your expected schema
            # For simplicity, we're returning the raw result here
            return result
        except Exception as e:
            logger.error(f"Error extracting invoice data with LLM: {str(e)}")
            raise
    
    def analyze_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze invoice data to identify potential issues
        
        Args:
            invoice_data: Structured invoice data
            
        Returns:
            Analysis results with identified issues
        """
        if not self.client:
            logger.error("Groq client not initialized. Cannot analyze invoice.")
            raise ValueError("Groq client not initialized")
        
        prompt_old = f"""
        You are an AI assistant specialized in analyzing energy invoices.
        Analyze this energy invoice data and identify any potential issues or anomalies:
        
        {invoice_data}
        
        Consider the following aspects in your analysis:
        1. Is the energy consumption unusually high compared to typical usage?
        2. Are there any unusual charges or fees?
        3. Are the rates competitive based on current market rates?
        4. Are there any calculation errors in the invoice?
        5. Are there any signs of potential energy waste?
        
        Return your analysis in a structured JSON format with these keys:
        issues (array of identified issues), severity (high, medium, low for each issue)
        """

        prompt = f"""
        Vous êtes un assistant IA spécialisé dans l'analyse des factures d'énergie.
En vous basant *intégralement* sur les "Problèmes observés" et leurs "Effets sur la facture" décrits dans le document "Essentiel pour l'optimisation des redevances électriques", analysez les données de cette facture d'énergie et identifiez toute anomalie ou problème potentiel :

{invoice_data}

Votre analyse doit spécifiquement rechercher les problèmes suivants, tels que définis dans le document de référence :

1.  **Facteur de puissance (cos φ) < 0.93**: Y a-t-il des signes de "Pénalités sur la puissance réactive" ou des données suggérant un facteur de puissance faible ?
2.  **Puissance appelée > 110 % de la puissance souscrite**: Des "Pénalités de dépassement" sont-elles appliquées, indiquant que la puissance appelée a excédé significativement la puissance souscrite ?
3.  **Puissance souscrite trop élevée par rapport à la puissance réellement appelée**: Y a-t-il un "Surcoût mensuel inutile" potentiel dû à une puissance souscrite qui semble excessive par rapport à l'historique de consommation ou la puissance maximale appelée ?
4.  **Consommation concentrée durant les heures pleines (HP)**: La répartition de la consommation indique-t-elle une concentration significative en "Heures Pleines", entraînant un "Coût élevé de l'énergie" ?

Retournez votre analyse dans un format JSON structuré avec ces clés :
`issues` (un tableau d'objets, où chaque objet décrit un problème identifié), `severity` (la gravité pour chaque problème : "high", "medium", "low"). Chaque objet dans le tableau `issues` doit avoir une clé `description` pour le problème et une clé `severity`.

retournez juste un json, sans texte, sans remarques, sans ```json juste le json , toute la reponse doit etre en francais
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that analyzes energy invoices for issues. you return just a valid json, do not put ```json in first or at the end of the response , just put the json"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            # print('second response',response)
            result = response.choices[0].message.content
            print('result',result)
            result = extract_json_from_response(result)
            print('result after extract',result)
            return result
        except Exception as e:
            logger.error(f"Error analyzing invoice with LLM: {str(e)}")
            raise
    
    def generate_recommendations(self, invoice_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate recommendations based on invoice data and analysis
        
        Args:
            invoice_data: Structured invoice data
            analysis: Analysis results with identified issues
            
        Returns:
            Recommendations for optimizing energy usage and costs
        """
        if not self.client:
            logger.error("Groq client not initialized. Cannot generate recommendations.")
            raise ValueError("Groq client not initialized")
        
        prompt_old = f"""
        You are an AI assistant specialized in providing energy optimization recommendations.
        Based on this energy invoice data and analysis, provide recommendations for optimizing energy usage and reducing costs:
        
        Invoice data:
        {invoice_data}
        
        Analysis:
        {analysis}
        
        Provide specific, actionable recommendations that could help the customer:
        1. Reduce energy consumption
        2. Lower costs
        3. Improve energy efficiency
        4. Address any issues identified in the analysis
        
        Also estimate potential savings (as a percentage and dollar amount) if recommendations are followed.
        
        Return your recommendations in a structured JSON format with these keys:
        recommendations (array of recommendation strings), potential_savings (estimated dollar amount), 
        efficiency_score (0-100 rating of current efficiency)
        """

        prompt = f"""
        Vous êtes un assistant IA spécialisé dans la fourniture de recommandations d'optimisation énergétique.
En vous basant sur les données de cette facture d'énergie et l'analyse fournie, fournissez des recommandations pour optimiser l'utilisation de l'énergie et réduire les coûts.

Données de la facture :
{invoice_data}

Analyse :
{analysis}

Pour chaque problème identifié dans l'analyse (`analysis.issues`), trouvez la correspondance ci-dessous et formulez une recommandation spécifique et actionable en vous basant sur l' "Action recommandée" et l' "Explication détaillée" correspondantes.

**Liste des problèmes et des actions recommandées (tirées du document "Essentiel pour l'optimisation des redevances électriques") :**

*   **Si l'analyse identifie un problème lié au "Facteur de puissance (cos φ) < 0.93" ou des "Pénalités sur la puissance réactive" :**
    *   **Action recommandée :** "Installer des batteries de condensateurs"
    *   **Explication détaillée :** "Un cos φ faible signifie que vous tirez plus de puissance apparente que nécessaire. Cela surcharge les équipements et le réseau. La correction réduit la puissance réactive et évite des pénalités mensuelles. L'objectif est d'atteindre un cos φ à ≥ 0.93 (idéalement 0.95-0.98)."
    *   **Recommandation à formuler :** l'installation de batteries de condensateurs en expliquant que cela corrigera le facteur de puissance, réduira la puissance réactive et évitera les pénalités mensuelles.

*   **Si l'analyse identifie un problème lié à la "Puissance appelée > 110 % de la puissance souscrite" ou des "Pénalités de dépassement" :**
    *   **Action recommandée :** "Étalement des démarrages, gestion des appels de charge, dispositifs de lissage (peak shaving)"
    *   **Explication détaillée :** "Lorsque vous dépassez 1.1 × la puissance souscrite, vous êtes facturé pour le surplus. Il faut éviter les démarrages simultanés ou les pics inattendus (par exemple, compresseurs + convoyeurs). L'objectif est de réduire les pics de puissance."
    *   **Recommandation :** l'étalement des démarrages, une meilleure gestion des appels de charge et/ou l'utilisation de dispositifs de lissage (peak shaving) pour réduire les pics de puissance et éviter les surcoûts liés aux dépassements.

*   **Si l'analyse identifie un problème lié à la "Puissance souscrite trop élevée par rapport à la puissance réellement appelée" ou un "Surcoût mensuel inutile" :**
    *   **Action recommandée :** "Analyser les historiques de charge et ajuster la puissance souscrite"
    *   **Explication détaillée :** "La puissance souscrite est facturée même si elle n'est pas utilisée. Il est judicieux de la fixer légèrement au-dessus de la puissance maximale réellement consommée pour éviter les pénalités sans surpayer. L'objectif est de réduire la puissance souscrite au niveau optimal."
    *   **Recommandation :** analyser les historiques de charge pour ajuster la puissance souscrite au niveau optimal, en veillant à ce qu'elle soit légèrement supérieure à la puissance maximale réellement consommée pour éviter les frais inutiles.

*   **Si l'analyse identifie un problème lié à la "Consommation concentrée durant les heures pleines (HP)" ou un "Coût élevé de l'énergie" :**
    *   **Action recommandée :** "Transférer la consommation vers les heures creuses (HC) ou normales (HN) / Programmer les équipements pour fonctionner en HC"
    *   **Explication détaillée :** "Les heures pleines sont les plus coûteuses. En planifiant les usages énergétiques importants (non critiques) la nuit ou en HC, on réduit fortement la facture d'énergie sans modifier la production."
    *   **Recommandation :** transférer la consommation des équipements non critiques vers les heures creuses ou normales, en programmant leur fonctionnement pendant ces périodes moins coûteuses.

Estimez également les économies potentielles (en pourcentage et en montant monétaire) si les recommandations sont suivies. Si les données fournies ne permettent pas une estimation précise, vous pouvez indiquer `null` pour ces valeurs ou fournir une estimation basée sur des hypothèses générales (en mentionnant ces hypothèses si possible).
Attribuez également un `efficiency_score` (évaluation de 0 à 100 de l'efficacité actuelle) en fonction de la présence et de la gravité des problèmes identifiés.

Retournez vos recommandations dans un format JSON structuré avec ces clés :
`recommendations` (tableau de chaînes de caractères décrivant les recommandations), `potential_savings` (montant monétaire estimé),
`efficiency_score` (évaluation de 0 à 100 de l'efficacité actuelle).

retournez juste un json, sans texte, sans remarques, sans ```json juste le json , toute la reponse doit etre en francais
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that provides energy optimization recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                # max_tokens=1500
            )
            
            result = response.choices[0].message.content
            result = extract_json_from_response(result)
            print('result after extract',result)
            return result
        except Exception as e:
            logger.error(f"Error generating recommendations with LLM: {str(e)}")
            raise
