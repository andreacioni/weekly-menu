from .. import BASE_PATH

def create_module(app, api):
    
    from .resources import RecipeIngredientList, RecipeIngredientInstance
    
    api.add_resource(
        RecipeIngredientList,
        BASE_PATH + '/recipes/<string:recipe_id>/ingredients'
    )
    api.add_resource(
        RecipeIngredientInstance,
        BASE_PATH + '/recipes/<string:recipe_id>/ingredients/<string:ingredient_id>'
    )