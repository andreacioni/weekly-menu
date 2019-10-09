from .. import BASE_PATH

def create_module(app, api):
    
    from .resources import UserShoppingLists, UserShoppingList, UserShoppingListItems
    
    api.add_resource(
        UserShoppingLists,
        BASE_PATH + '/shopping-lists'
    )

    api.add_resource(
        UserShoppingList,
        BASE_PATH + '/shopping-lists/<string:shopping_list_id>'
    )

    api.add_resource(
        UserShoppingListItems,
        BASE_PATH + '/shopping-lists/<string:shopping_list_id>/items'
    )