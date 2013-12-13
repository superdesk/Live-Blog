define(function()
{
    return {
        ajaxMap: {
            'Collaborator/1': 
            {
                "Source": {"href": "Source/1", "Id": "1"}, 
                "Person": {"href": "Person/1", "Id": "1"},
                "Post": {"href": "Collaborator/1/Post"},
                "PublishedPost": {"href": "Collaborator/1/PublishedPost/"},
                "UnpublishedPost": {"href": "Collaborator/1/UnpublishedPost/"}, 
                "Id": "1", "Name": "Test User"
            },
            "Collaborator/1/Post":
            {
                "PostList": 
                [
                    {
                        "href": "Post/1", 
                        "Author": { "href": "Collaborator/1/", "Id": "1" }, 
                        "CreatedOn": "Jun 5, 2012 5:50:49 PM", 
                        "Creator": { "href": "User/1", "Id": "1" }, 
                        "Content": "Live Blog is a next-generation open source web tool for both individuals and teams to report live breaking news from anywhere.", 
                        "AuthorName": "Author 1", 
                        "PublishedOn": "Jun 5, 2012 5:50:49 PM", 
                        "Type": { "href": "PostType/quote", "Key": "quote" }, 
                        "Id": "1", 
                        "IsModified": "False"
                    }, 
                    {   
                        "href": "Post/2", 
                        "Author": { "href": "Collaborator/1", "Id": "1" }, 
                        "CreatedOn": "Jun 5, 2012 5:50:50 PM", 
                        "Creator": { "href": "User/1", "Id": "1" }, 
                        "Content": "That is all for today folks. Join us at GEN News World Media Summit to see Douglas Arellanes demoing the tool live.", 
                        "AuthorName": "User2", 
                        "PublishedOn": "Jun 5, 2012 5:50:50 PM",
                        "Type": { "href": "PostType/wrapup", "Key": "wrapup" }, 
                        "Id": "2", 
                        "IsModified": "False"
                    }
                ], 
                "total": "2"
            },
            'Post/1': { href: 'Post/1', Content: 'A' },
            'Post/2': { href: 'Post/2', Content: 'B' },
            'Post/3': { href: 'Post/3', Content: 'C' },
            "Collaborator/1/PublishedPost/":{ 'PostList': [{ href: 'Post/1', Content: 'A' },{ href: 'Post/2', Content: 'B' }] },
            //"my/Collaborator/1/Post/Published":{ 'PostList': [] },
            "Collaborator/1/PublishedPost/":{ 'PostList': [] },
            "Collaborator/1/UnpublishedPost/":
            {
                'PostList': [{ href: 'Post/1', Content: 'A' },{ href: 'Post/3', Content: 'C' }]
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
            "Person/2":
            {
                "Collaborator": {"href": "Person/2/Collaborator"}, 
                "FullName": "Test Person 2", 
                "Id": "2", 
                "FirstName": "Person", 
                "EMail": "le-person@email.com"
            },
            "Person/1/Collaborator":
            {
                
            },
            
            //"my/Person/1":
            "Person/1":
            {
                //"Collaborator": {"href": "my/Person/1/Collaborator"}, 
                "Collaborator": {"href": "Person/1/Collaborator"}, 
                "FullName": "Test Person", 
                "Id": "1", 
                "FirstName": "Person", 
                "EMail": "person@email.com"
            }
        }
    };
});