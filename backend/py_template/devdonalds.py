from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)


# Store your recipes here!
cookbook: Dict[str, Union[Recipe, Ingredient]] = {}


# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200





# [TASK 1] ====================================================================

def parse_handwriting(recipeName: str) -> Union[str | None]:
    
	"""
 	parse_handwriting takes in a recipeName and returns it in a form that is properly formatted.
  
	Args:
		recipeName (str): The raw recipe name string
  
	Returns:
		str or None:
			- If after parsing, there are more than 0 valid characters remaining, a cleaned recipe name is outputted.
			- If the input is 'None' or no valid letters remain after parsing, the function returns None.
   
	Examples:
		- parse_handwriting("Riz@z_RISO00tto!") returns 'Rizz Risotto'
		- parse_handwriting("1234!@#$") returns None (because no valid letters remain after cleaning)
	"""

	#replace all hyphens with a blank white space
	recipeName = recipeName.replace("-", " ")
 
	#replace all underscores with a blank white space
	recipeName = recipeName.replace("_", " ")
 
 
	"""
 	Remove all characters except for letters and spaces. 
 	The regex sub replaces all letters which are NOT (^ symbol) in A-Z (A, B, C, ...., Z) 
  	or a-z (a, b, c,..., z) or whitespace (spaces, tabs, etc.), with an empty string
   	"""
    
	recipeName = re.sub(r'[^A-Za-z\s]', '', recipeName)
 
	#convert everything to lowercase
	recipeName = recipeName.lower()
 
	#break the recipeName string into a list of substrings that are separated by whitespace.
	words = recipeName.split()
	
	
	capitalised_words = []
 
	for word in words:
		#capitalise each word in the 'words' list using capitalize() method
		capitalised_word = word.capitalize()
		#append each capitalised_word to the end of the capitalised_words list.
		capitalised_words.append(capitalised_word)
  
	#join each of the newly capitalised_words together, with a space in the middle
	recipeName = ' '.join(capitalised_words)
 
 
	if len(recipeName) <= 0:
		return None
	else:
		return recipeName





# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
    data = request.get_json(silent=True)
    
    #if the incoming request is not a dictionary, return error
    if not isinstance(data, dict):
        return ('', 400)
    
    #get the value of the "entry" key from data dict. If the value is not a dict, return error
    entry = data.get("entry", data)
    if not isinstance(entry, dict):
        return ('', 400)
    
    #extract values ('type (str)' and 'name (str)') from the entry dict
    entry_type = entry.get("type")
    name = entry.get("name")
    
    #entries can only be either a 'recipe' or an 'ingredient'
    if entry_type not in ("recipe", "ingredient"):
        return ('', 400)
    
    #also, the names need to be valid strings.
    if not isinstance(name, str) or not name.strip():
        return ('', 400)
    
    #check for duplicate names
    if name in cookbook:
        return ('', 400)
    
    #ingredients case
    if entry_type == "ingredient":
        cook_time = entry.get("cookTime")
        if not isinstance(cook_time, int) or cook_time < 0:
            return ('', 400)
        
        cookbook[name] = Ingredient(name=name, cook_time=cook_time)
    
    #recipes case
    else:
        required_items_data = entry.get("requiredItems")
        
        #requiredItems must be a list
        if not isinstance(required_items_data, list):
            return ('', 400)
        
        
        #intialise an empty set and an empty list
        seen_names = set()
        required_items_list = []
        
        for item in required_items_data:
            
            #each item within the required_items_list needs to be a dict
            if not isinstance(item, dict):
                return ('', 400)
            
            #get values of keys in each item dict
            item_name = item.get("name")
            quantity = item.get("quantity")
            
            #each item_name needs to be a valid string
            if not isinstance(item_name, str) or not item_name.strip():
                return ('', 400)
            
            #if current item_name in the loop is already in the seen_names set, return error.
            if item_name in seen_names:
                return ('', 400)
            
            #add current item_name to the seen_names set (to prevent future duplicates)
            seen_names.add(item_name)
            
            #if quantity is not int, return error
            if not isinstance(quantity, int):
                return ('', 400)
            
            #appends a new instance of RequiredItem class to the required_items_list
            required_items_list.append(RequiredItem(name=item_name, quantity=quantity))
        
        #creates new instance of Recipe class and stores it in the cookbook dict
        cookbook[name] = Recipe(name=name, required_items=required_items_list)
    
    return ('', 200)






# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
    recipe_name = request.args.get("name")
    
    #if recipe_name is not a valid string return error
    if not isinstance(recipe_name, str) or not recipe_name.strip():
        return ('', 400)
    
    #check if recipe exists in the cookbook
    valid_recipe = cookbook.get(recipe_name)
    if not valid_recipe:
        return ('', 400)
    
    #check the valid_recipe is actually a recipe (not an ingredient)
    if not isinstance(valid_recipe, Recipe):
        return ('', 400)
    
    #track ingredients and total time needed to prepare them
    ingredients = {}  # name -> quantity
    total_time = 0
    
    def process_item(name: str, multiplier: int = 1):
        nonlocal total_time
        
        item = cookbook.get(name)
        
        #check if item exists
        if not item:
            raise ValueError("Item not found")
        
        #If the RequiredItem item is an ingredient
        if isinstance(item, Ingredient):
            #example: If 'Egg' has cook_time=3 and there are 4 eggs, we add 3*4=12 to the total_time
            total_time += item.cook_time * multiplier
            
            #add the multiplier to the ingredient's total quantity
            ingredients[name] = ingredients.get(name, 0) + multiplier
        #If the RequiredItem item is itself a recipe
        else:
            #for each required item, recursively call process_item()
            for req in item.required_items:
                process_item(req.name, multiplier * req.quantity)
    
    try:
        process_item(recipe_name)
    except ValueError:
        return ('', 400)
    
    #format ingredients_list response
    ingredients_list = [
        {"name": name, "quantity": qty}
        for name, qty in ingredients.items()
    ]
    
    #return JSON response object
    return jsonify({
        "name": recipe_name,
        "cookTime": total_time,
        "ingredients": ingredients_list
    }), 200



# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
