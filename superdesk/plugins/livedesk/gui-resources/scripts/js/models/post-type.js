define(['gizmo'], function(giz)
{
    var PostType = giz.Model.extend();
    // Post Type
    return new giz.Collection(PostType);
});