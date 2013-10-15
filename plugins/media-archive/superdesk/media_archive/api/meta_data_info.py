'''
Created on Jan 21, 2013

@package: superdesk media archive
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Creates the model that will be used for multi-plugins queries.
'''

from ally.api.config import query
from superdesk.media_archive.api.domain_archive import modelArchive
from superdesk.media_archive.api.criteria import AsIn, AsLikeExpressionOrdered
from superdesk.media_archive.api.meta_info import MetaInfoBase
from ally.api.criteria import AsEqual
from superdesk.media_archive.api.meta_data import MetaDataBase
from ally.support.api.entity_ided import Entity

# --------------------------------------------------------------------

@modelArchive
class MetaDataInfo(MetaDataBase, MetaInfoBase, Entity):
    '''
    (MetaDataBase, MetaInfoBase)
    Provides the meta data information that is provided by the user.
    '''

# --------------------------------------------------------------------

@query(MetaDataInfo)
class QMetaDataInfo:
    '''
    The query for the meta data info models for all texts search.
    '''
    all = AsLikeExpressionOrdered
    type = AsIn
    language = AsEqual
