define('providers/colabs', ['providers', 'jquery', 'jquery/rest'],
function(providers, $)
{
    providers.colabs = 
    {
        className: 'big-icon-collaborators',       
        init: function(theBlog) 
        {              
            var blog = new $.rest(theBlog).get('BlogCollaborator').done(function(colabList)
            {
                var colabsList = [];
                $(this.extractListData(colabList)).each(function()
                { 
                    new $.rest(this.href)
                    .xfilter('Collaborator.Person.FirstName,Collaborator.Person.LastName,Collaborator.Person.Id,Collaborator.Post')
                    .done(function(colab)
                    {
                       colabsList.push(colab);
                       new $.rest(colab.Collaborator.Post.Post.href)
                       .xfilter('Id, Content, CreatedOn, PublishedOn')
                       .done(function(postList)
                       {
                          console.log(postList);
                       });
                    });
                });
            });
        }
    };
    return providers;
});