from __future__ import annotations

import json
import logging
from typing import Optional, Union

from astropy.table import Table
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass

ATMOSPHERIC_DEFAULT_LIMIT = 10000


class AtmosphericSpectroscopyClass:
    """
    The atmospheric spectroscopy class.
    Use to retrieve data from the atmospheric spectroscopy module.

    .. tip::

        A catalog instance is already provided, to use it:

        .. code-block:: python

            from dace_query.atmosphericSpectroscopy import AtmosphericSpectroscopy

    """
    
    def __init__(self, dace_instance: Optional[DaceClass] = None):
        """
        Create a configurable atmospheric spectroscopy object which uses a specified dace instance.

        :param dace_instance: A dace object
        :type dace_instance: DaceClass

        .. code-block:: python

            from dace_query.atmosphericSpectroscopy import AtmosphericSpectroscopyClass
            atmospheric_spectroscopy_instance = AtmosphericSpectroscopyClass()

        """
        self.__OBSERVATION_API = 'obs-webapp'

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"atmospheric-spectroscopy-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def query_database(self,
                       limit: Optional[int] = ATMOSPHERIC_DEFAULT_LIMIT,
                       filters: Optional[dict] = None,
                       sort: Optional[dict] = None,
                       output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the atmospheric spectroscopy database to retrieve data in the chosen format.

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).


        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: dict
        :param sort: Sort order to apply to the query
        :type sort: Optional[dict]
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting the full atmospheric spectroscopy database
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.atmosphericSpectroscopy import AtmosphericSpectroscopy
                values =  AtmosphericSpectroscopy.query_database()
            
        """

        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__OBSERVATION_API,
                endpoint='observation/search/atmosphericSpectroscopy',
                params={
                    'limit': str(limit),
                    'filters': json.dumps(filters),
                    'sort': json.dumps(sort)}
            ), output_format=output_format)


AtmosphericSpectroscopy: AtmosphericSpectroscopyClass = AtmosphericSpectroscopyClass()
"""

This is a singleton instance of the :class:`AtmosphericSpectroscopyClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.atmosphericSpectroscopy import AtmosphericSpectroscopy
"""
