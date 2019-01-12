"""DNS Authenticator for GoDaddy DNS."""
import logging

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common
from certbot.plugins import dns_common_lexicon
from certbot.plugins.dns_common_lexicon import LexiconClient
from lexicon.providers import godaddy

logger = logging.getLogger(__name__)



@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for GoDaddy

    This Authenticator uses the Gadaddy API to fulfill a dns-01 challenge.

    Inspired by certbot-dns-dnsimple
    """

    description = 'Obtain certificates using a DNS TXT record on GoDaddy.'
    ttl = 60

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None
        self._client = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=30)
        add('credentials', help='GoDaddy credentials INI file.')

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the GoDaddy API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'GoDaddy credentials INI file',
            {
                'key': 'GoDaddy production api key',
                'secret': 'GoDaddy production api secret',
            }
        )

    def _perform(self, domain, validation_name, validation):
        self._get_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        print('perform cleanup')
        self._get_client().del_txt_record(domain, validation_name, validation)

    def _get_client(self) -> LexiconClient:
        if not self._client:
            self._client = _GoDaddyLexiconClient(
                self.credentials.conf('key'),
                self.credentials.conf('secret'), self.ttl)
        return self._client


class _GoDaddyLexiconClient(dns_common_lexicon.LexiconClient):
    """
    Encapsulates all communication with GoDaddy via Lexicon.
    """

    def __init__(self, key, secret, ttl):
        super(_GoDaddyLexiconClient, self).__init__()

        config = {
            'provider_name': 'godaddy',
            'ttl': ttl,
            'auth_key': key,
            'auth_secret': secret,
        }

        self.provider = godaddy.Provider(config)

    def _handle_http_error(self, e, domain_name):
        hint = None
        if str(e).startswith('401 Client Error: Unauthorized for url:'):
            hint = 'Is your API token value correct?'

        return errors.PluginError('Error determining zone identifier for {0}: {1}.{2}'
                                  .format(domain_name, e, ' ({0})'.format(hint) if hint else ''))
