import requests

def get_random_meal():
    try:
        response = requests.get("https://www.themealdb.com/api/json/v1/1/random.php")
        response.raise_for_status()
        data = response.json()
        meal = data['meals'][0]
        
        meal_name = meal['strMeal']
        meal_image = meal['strMealThumb']
        meal_instructions = meal['strInstructions']
        
        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}')
            measure = meal.get(f'strMeasure{i}')
            if ingredient and measure:
                ingredients.append(f"{ingredient} - {measure}")
        
        ingredient_list = '\n'.join(ingredients)
        
        return {
            'name': meal_name,
            'image': meal_image,
            'instructions': meal_instructions,
            'ingredients': ingredient_list
        }
    except requests.RequestException as e:
        return {'error': 'Не удалось получить рецепт'}