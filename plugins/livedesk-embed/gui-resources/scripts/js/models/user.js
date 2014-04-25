/*!
 * Model class for the User
 *   will register into Gizmo.Register the class defined
 */
define([ 'gizmo/superdesk' ], function( Gizmo ) {
	return Gizmo.Model.extend
	( {}, { register: 'User' } );
});
