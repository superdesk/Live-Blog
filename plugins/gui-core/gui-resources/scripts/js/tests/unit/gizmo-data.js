define(function()
{
    return {
        ajaxMap: {
            'Collaborator/1': 
            {
                "Source": {"href": "Source/1", "Id": "1"}, 
                "Person": {"href": "Person/1", "Id": "1"},
                "Post": {"href": "Collaborator/1/Post"},
                "PostPublished": {"href": "Collaborator/1/Post/Published"},
                "PostUnpublished": {"href": "Collaborator/1/Post/Unpublished"}, 
                "Id": "1", "Name": "Test User"
            },
            "Collaborator/1/Post":
            {
                
            },
            "Collaborator/1/Post/Published":
            {
                
            },
            "Collaborator/1/Post/Unpublished":
            {
                
            },
            
            
            "Source/1": 
            {
                "Name": "internal", 
                "URI": {"href": ""}, 
                "IsModifiable": "False", 
                "Collaborator": {"href": "Source/1/Collaborator"}, 
                "Type": {"href": "SourceType/", "Key": ""}, 
                "Id": "2"
            },
            "Source/1/Collaborator": 
            {
                
            },
            
            "Person/1":
            {
                "Collaborator": {"href": "Person/1/Collaborator"}, 
                "FullName": "Test Person", 
                "Id": "1", 
                "FirstName": "Person", 
                "EMail": "person@email.com"
            },
            "Person/1/Collaborator":
            {
                
            }
        }
    };
});