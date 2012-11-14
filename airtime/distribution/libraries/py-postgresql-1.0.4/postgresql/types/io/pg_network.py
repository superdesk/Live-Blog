from .. import INETOID, CIDROID, MACADDROID
from . import lib

oid_to_io = {
	MACADDROID : (lib.macaddr_pack, lib.macaddr_unpack, str),
	CIDROID : (lib.net_pack, lib.cidr_unpack, str),
	INETOID : (lib.net_pack, lib.net_unpack, str),
}

oid_to_type = {
	MACADDROID : str,
	CIDROID : str,
	INETOID : str,
}
