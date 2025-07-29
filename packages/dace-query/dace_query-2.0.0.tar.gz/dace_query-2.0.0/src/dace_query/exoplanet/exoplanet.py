from __future__ import annotations

import json
import logging
from typing import Union, Optional

from astropy.table import Table
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass

EXOPLANET_DEFAULT_LIMIT = 10000
PLANETS_CATALOG_NAME = 'planets'
ATREIDES_CATALOG_NAME = 'atreides'

class ExoplanetClass:
    """
    The exoplanet class.
    Use to retrieve data from the exoplanet module.

    .. tip::
    
        An exoplanet instance is already provided, to use it:

        .. code-block:: python

            from dace_query.exoplanet import Exoplanet

    """
    __EXOPLANET_ENDPOINT = 'ExoplanetAPI/exoplanetDatabase'

    def __init__(self, dace_instance: Optional[DaceClass] = None):
        """
        Create a configurable exoplanet object which uses a specified dace instance.

        :param dace_instance: A dace object
        :type dace_instance: Optional[DaceClass]

        .. code-block:: python

            from dace_query.exoplanet import ExoplanetClass
            exoplanet_instance = ExoplanetClass()

        """

        self.__EXOPLANET_API = 'exo-webapp'

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"exoplanet-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def query_database(self,
                       catalog: Optional[str] = PLANETS_CATALOG_NAME,
                       limit: Optional[int] = EXOPLANET_DEFAULT_LIMIT,
                       filters: Optional[dict] = None,
                       sort: Optional[dict] = None,
                       output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the exoplanet database to retrieve data in the chosen format.

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        You may specify the catalog to query using the ``catalog`` parameter.
        
        
        .. dropdown:: Available catalogs
            :color: info
            :icon: list-unordered
            :open:
            
            * - ``'planets'`` : The PlanetS exoplanet database **(selected by default)**
            * - ``'atreides'`` : The Atreides exoplanet database

        :param catalog: Name of the catalog to query (``'planets'`` or ``'atreides'``)
        :type catalog: Optional[str]
        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param sort: Sort order to apply to the query
        :type sort: Optional[dict]
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict
    
    
        .. dropdown:: Getting all exoplanet data
            :color: success
            :icon: code-square

            .. code-block:: python
            
                from dace_query.exoplanet import Exoplanet
                values = Exoplanet.query_database()
                
        .. dropdown:: Getting data from a specific catalog
            :color: success
            :icon: code-square

            .. code-block:: python
            
                from dace_query.exoplanet import Exoplanet
                values = Exoplanet.query_database(catalog='atreides')
        """

        if catalog not in [PLANETS_CATALOG_NAME, ATREIDES_CATALOG_NAME]:
            raise ValueError(f"Catalog {catalog} does not exist. Please use {PLANETS_CATALOG_NAME} or {ATREIDES_CATALOG_NAME}.")

        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__EXOPLANET_API,
                endpoint=f'search/{catalog}',
                params={
                        'limit': str(limit),
                        'filters': json.dumps(filters),
                        'sort': json.dumps(sort)}
            ), output_format=output_format)


Exoplanet: ExoplanetClass = ExoplanetClass()
"""
This is a singleton instance of the :class:`ExoplanetClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.exoplanet import Exoplanet
"""