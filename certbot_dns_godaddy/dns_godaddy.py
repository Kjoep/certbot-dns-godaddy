"""DNS Authenticator for GoDaddy DNS."""
import logging

import zope.interface

from certbot import interfaces
from certbot.plugins import dns_common
from godaddypy import Account, Client

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for GoDaddy

    This Authenticator uses the Gadaddy API to fulfill a dns-01 challenge.

    Inspired by certbot-dns-dnsimple
    """

    description = 'Obtain certificates using a DNS TXT record on GoDaddy.'
    ttl = 600

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None
        self._client = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=30)
        add('credentials', help='Godaddy credentials INI file.')

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
        self._get_client().add_record(domain, {
            'type': 'TXT',
            'name': self._unsuffix(validation_name, f'.{domain}'),
            'data': validation,
            'ttl': self.ttl
        })

    def _cleanup(self, domain, validation_name, validation):
        self._get_client().delete_records(domain, self._unsuffix(validation_name, f'.{domain}'), record_type='TXT')

    def _get_client(self) -> Client:
        if not self._client:
            account = Account(api_key=self.credentials.conf('key'), api_secret=self.credentials.conf('secret'))
            self._client = Client(account)
        return self._client

    def _unsuffix(self, record: str, suffix: str):
        """ GoDaddy wants to have only the first part of the domain record (so for a.b.com, for domain b.com,
            only 'a'. """

        if not record.endswith(suffix):
            logger.warning(f'Expected record {record} to contain domain suffix, but it did not')
            return record
        return record[:-len(suffix)]
