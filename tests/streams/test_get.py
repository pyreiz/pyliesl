def test_get_hostip_normal():
	from liesl.streams import get_ip_adress, get_localhostname
	assert get_ip_adress() != "123.4.567.890"
	assert  get_localhostname() != "sphinx-doc"

from tempenv import TemporaryEnvironment
@TemporaryEnvironment({"DOC": "TRUE"})
def test_get_hostip_docenv():
	from liesl.streams import get_ip_adress, get_localhostname
	assert get_ip_adress() == "123.4.567.890"
	assert  get_localhostname() == "sphinx-doc"
