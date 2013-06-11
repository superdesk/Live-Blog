define(['backbone', 'gizmo/superdesk', config.guiJs('livedesk', 'models/sync')],
function(Backbone, Gizmo, SyncModel) {
    return Backbone.Collection.extend({
        model: SyncModel,
        xfilter: {'X-Filter': 'Id, Auto, Source.Id, CId'},

        parse: function(response) {
            return response.SyncList;
        },

        findSource: function(sourceId) {
            return this.findWhere({SourceId: sourceId});
        },

        isAuto: function(sourceId) {
            var sync = this.findSource(sourceId);
            return Boolean(sync) && sync.get('Auto') === 'True';
        },

        isPaused: function(sourceId) {
            var sync = this.findSource(sourceId);
            return Boolean(sync) && sync.get('Auto') === 'False';
        },

        getLastSyncId: function(sourceId) {
            var sync = this.findSource(sourceId);
            return sync && sync.get('CId');
        }
    });
});
