import openai
from app.models import ApiResponse
import os
import logging
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
llm = OpenAI(model="gpt-4o-mini",api_key=os.getenv("OPENAI_API_KEY"))

async def correct_scandinavian_name(name, country):
    """
    Corrects poorly transliterated Scandinavian names based on country using a hybrid approach.
    First applies character mappings, then uses LLM if no changes were detected.
    
    Args:
        name (str): The name to correct
        country (str): The Scandinavian country (Sweden, Norway, Denmark, Finland, Iceland)
        
    Returns:
        ApiResponse: The corrected name and metadata
    """
    try:
        country = country.lower()
    
        # Complete character mappings for each country
        mappings = {
            'sweden': {
                # Common transliterations
                'ae': 'ä', 'oe': 'ö', 'aa': 'å',
                'Ae': 'Ä', 'Oe': 'Ö', 'Aa': 'Å',
                'AE': 'Ä', 'OE': 'Ö', 'AA': 'Å',
                # Less common but possible
                'a:': 'ä', 'o:': 'ö',
                'A:': 'Ä', 'O:': 'Ö',
            },
            'norway': {
                # Common transliterations
                'ae': 'æ', 'oe': 'ø', 'aa': 'å',
                'Ae': 'Æ', 'Oe': 'Ø', 'Aa': 'Å',
                'AE': 'Æ', 'OE': 'Ø', 'AA': 'Å',
                # Less common but possible
                'a:': 'æ', 'o:': 'ø',
                'A:': 'Æ', 'O:': 'Ø',
                # Additional Norwegian characters
                'o/': 'ø', 'O/': 'Ø',
            },
            'denmark': {
                # Common transliterations
                'ae': 'æ', 'oe': 'ø', 'aa': 'å',
                'Ae': 'Æ', 'Oe': 'Ø', 'Aa': 'Å',
                'AE': 'Æ', 'OE': 'Ø', 'AA': 'Å',
                # Less common but possible
                'a:': 'æ', 'o:': 'ø',
                'A:': 'Æ', 'O:': 'Ø',
                # Additional Danish characters
                'o/': 'ø', 'O/': 'Ø',
            },
            'finland': {
                # Finland has Swedish as an official language, so similar mappings
                'ae': 'ä', 'oe': 'ö', 'aa': 'å',
                'Ae': 'Ä', 'Oe': 'Ö', 'Aa': 'Å',
                'AE': 'Ä', 'OE': 'Ö', 'AA': 'Å',
                # Less common but possible
                'a:': 'ä', 'o:': 'ö',
                'A:': 'Ä', 'O:': 'Ö',
            },
            'iceland': {
                # Vowels with acute accents
                'aa': 'á', 'ee': 'é', 'ii': 'í', 'oo': 'ó', 'uu': 'ú', 'yy': 'ý',
                'Aa': 'Á', 'Ee': 'É', 'Ii': 'Í', 'Oo': 'Ó', 'Uu': 'Ú', 'Yy': 'Ý',
                'AA': 'Á', 'EE': 'É', 'II': 'Í', 'OO': 'Ó', 'UU': 'Ú', 'YY': 'Ý',
                
                # Special Icelandic characters
                'ae': 'æ', 'Ae': 'Æ', 'AE': 'Æ',
                'oe': 'ö', 'Oe': 'Ö', 'OE': 'Ö',
                
                # Thorn and Eth
                'th': 'þ', 'Th': 'Þ', 'TH': 'Þ',
                'd-': 'ð', 'D-': 'Ð',
                'dh': 'ð', 'Dh': 'Ð', 'DH': 'Ð',
            }
        }
        
        if country not in mappings:
            valid_countries = ', '.join(mappings.keys())
            return ApiResponse(
                status_code=400,
                message=f"Error: '{country}' is not a supported Scandinavian country. Choose from: {valid_countries}.",
                data={}
            )
        
        # Apply character replacements
        # Sort by length of pattern (longest first) to handle overlapping patterns correctly
        sorted_patterns = sorted(mappings[country].items(), key=lambda x: len(x[0]), reverse=True)
        
        original_name = name
        corrected_name = name
        
        for pattern, replacement in sorted_patterns:
            corrected_name = corrected_name.replace(pattern, replacement)
        
        # Check if any corrections were made
        if corrected_name == original_name:
            # No changes made by the mapping function, let's use the LLM
            logger.info(f"No changes made by mapping for '{name}', calling LLM")
            corrected_name = await call_llm_for_correction(name, country)
            method = "LLM"
        else:
            method = "Mapping"
            
        return ApiResponse(
            status_code=200,
            message="Name correction completed successfully!",
            data={
              "original_name": original_name,
                "corrected_name": corrected_name,
                "country": country,
                "correction_method": method
            }
        )

    except Exception as e:
        logger.error(f"Error in name correction: {e}", exc_info=True)
        return ApiResponse(
            status_code=500,
            message="Server error occurred during name correction.",
            data={"error": str(e)}
        )

async def call_llm_for_correction(name, country):
    country_contexts = {
        'sweden': "Swedish names often contain characters like ä, ö, å. Common transliterations that need correction include: 'ae'→'ä', 'oe'→'ö', 'aa'→'å'.",
        'norway': "Norwegian names often contain characters like æ, ø, å. Common transliterations that need correction include: 'ae'→'æ', 'oe'→'ø', 'aa'→'å'.",
        'denmark': "Danish names often contain characters like æ, ø, å. Common transliterations that need correction include: 'ae'→'æ', 'oe'→'ø', 'aa'→'å'.",
        'finland': "Finnish names (including Swedish-Finnish) often contain characters like ä, ö, å. Common transliterations that need correction include: 'ae'→'ä', 'oe'→'ö', 'aa'→'å'.",
        'iceland': "Icelandic names often contain characters like á, é, í, ó, ú, ý, æ, ö, þ, ð. Common transliterations that need correction include: 'th'→'þ', 'dh'→'ð', 'ae'→'æ', 'oe'→'ö', vowel doubling for acute accents (e.g., 'aa'→'á')."
    }
    context = country_contexts.get(country, "")
    system_prompt = f"""
    You are a specialist in correcting transliterated Scandinavian names special cases to their proper form with correct diacritical marks and special characters.
    ALWAYS handle these specific examples correctly (memorize them!):
    | Input Name | Country   | Expected Output |
    |------------|-----------|-----------------|
    | Ake        | Sweden    | Åke             |
    | Gosta      | Sweden    | Gösta           |
    | Oskar      | Iceland   | Óskar           |
    | Tord       | Iceland   | Þord            |
    | Moose      | Denmark   | Møse            |
    Your task:
    - Do not explain; return only the corrected name.
    - Handle the similar special cases patterns as provided above.
    Return only the corrected name. If no correction is needed, return the input unchanged.
    {context}
    """
    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=f"Please correct this {country.capitalize()} name: {name}")
    ]
    response = await llm.achat(messages)
    corrected_name = response.message.content.strip()
    return corrected_name