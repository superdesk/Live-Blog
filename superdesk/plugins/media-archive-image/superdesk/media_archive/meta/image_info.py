'''
Created on Apr 18, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media image info API.
'''

from ..api.image_info import ImageInfo
from .meta_info import MetaInfo
from ally.container.binder_op import validateManaged
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import meta

# --------------------------------------------------------------------

class MetaInfoMapped(Base, MetaInfo):

    def validate(self):
        o sa fie un singur media data service archive care foloseste file systzem:
            salveaza fisierul local in pathul cunoscut
            notifica data handlerurile de noul fisier dand si locatia fisireului in file system.
        o sa fie un singur thumbnail service unde faci upload la thumbnail si care se ocupa de resizing foloseste file systzem
        fara sa foloseasca un CDM si face resizing on demand bazat pe o lista cunoscuta de resizing. o sa fie un URL
        atasat de meta data ptr thumb si cat se cere thumbu o sa se specifice thumb size, eventual de facut o entitate
        pentru thumb care sa aiba un id unique si sa poate fi folosti ca referinta la upload, asta pentru cazul in care
        folosesti acelasi thumb pentru mai multe meta data si inclusiv daca se face sql pentru selectarea unui thumb
        tot merita, deci ideea ii sa folosim REST aproach si sa nu complicam lucrurile cu tot felu de procese.

        Ideea i ca daca folosim CDM ii complicat procseul si atunci ii mai usor ca serviciul the data si thumbs sa lucreze
        direct cu file system, ele putand fi distrbuite daca ii cazul sau facute implementari pe baza la altfel de
        structuri.



        de facut validatra astfel incat sa nu poti insera meta info pentru alte meta data types, tre facut cu
        declarative base
        de continuat cu image media si dupa aia de facut resize

table = Table('archive_image_info', meta,
              Column('fk_meta_info_id', ForeignKey(MetaInfo.Id), primary_key=True, key='Id'),
              Column('caption', String(255), nullable=False, key='Caption'),
              mysql_engine='InnoDB', mysql_charset='utf8')

ImageInfo = mapperModel(ImageInfo, table, exclude=['MetaData'], inherits=MetaInfo)
validateManaged(ImageInfo.MetaData)
