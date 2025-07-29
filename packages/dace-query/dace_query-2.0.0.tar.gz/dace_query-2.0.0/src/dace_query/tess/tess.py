from __future__ import annotations

import json
import logging
from typing import Union, Optional

from astropy.coordinates import SkyCoord, Angle
from astropy.table import Table
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass

TESS_DEFAULT_LIMIT = 10000


class TessClass:
    """
    The tess class.
    Use to retrieve data from the tess module.

    .. tip::
    
        A tess instance is already provided, to use it:
        
        .. code-block:: python
        
            from dace_query.tess import Tess
    """

    def __init__(self, dace_instance: Optional[DaceClass] = None):
        """
        Create a configurable tess instance.

        :param dace_instance: A dace object
        :type dace_instance: Optional[DaceClass]

        .. code-block:: python

            from dace_query.tess import TessClass
            tess_instance = TessClass()
        """
        self.__TESS_API = 'tess-webapp'

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"tess-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def query_database(self,
                       limit: Optional[int] = TESS_DEFAULT_LIMIT,
                       filters: Optional[dict] = None,
                       sort: Optional[dict] = None,
                       output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the tess database to retrieve data in the chosen format.

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param sort: Sort order to apply to the query
        :type sort: Optional[dict]
        :param output_format: The desired data in the chosen output format
        :type output_format: Optional[str]
        :return: A dict containing lists of values for each visit
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting all available observations
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.tess import Tess
                values = Tess.query_database()
        """
        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__TESS_API,
                endpoint='search',
                params={
                    'limit': str(limit),
                    'filters': json.dumps(filters),
                    'sort': json.dumps(sort)
                }
            ), output_format=output_format
        )
    
    
    def query_toi_catalog(self,
                    limit: Optional[int] = TESS_DEFAULT_LIMIT,
                    filters: Optional[dict] = None,
                    sort: Optional[dict] = None,
                    output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the Tess Object of Interest (TOI) catalog to retrieve data in the chosen format.

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param sort: Sort order to apply to the query
        :type sort: Optional[dict]
        :param output_format: The desired data in the chosen output format
        :type output_format: Optional[str]
        :return: A dict containing lists of values for each target in the TOI catalog
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting the TOI catalog
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.tess import Tess
                values = Tess.query_toi_catalog()
        """
        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__TESS_API,
                endpoint='catalog/toi',
                params={
                    'limit': str(limit),
                    'filters': json.dumps(filters),
                    'sort': json.dumps(sort)
                }
            ), output_format=output_format
        )


    def query_tic_catalog(self,
                    limit: Optional[int] = TESS_DEFAULT_LIMIT,
                    filters: Optional[dict] = None,
                    sort: Optional[dict] = None,
                    output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the Tess Input Catalog (TIC) to retrieve data in the chosen format.

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param sort: Sort order to apply to the query
        :type sort: Optional[dict]
        :param output_format: The desired data in the chosen output format
        :type output_format: Optional[str]
        :return: A dict containing lists of values for each target in the TIC
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting the TIC catalog
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.tess import Tess
                values = Tess.query_tic_catalog()
        """
        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__TESS_API,
                endpoint='catalog/tic',
                params={
                    'limit': str(limit),
                    'filters': json.dumps(filters),
                    'sort': json.dumps(sort)
                }
            ), output_format=output_format
        )

    def query_region(self,
                     sky_coord: SkyCoord,
                     angle: Angle,
                     limit: Optional[int] = TESS_DEFAULT_LIMIT,
                     filters: Optional[dict] = None,
                     output_format: Optional[str] = None,
                     catalog: Optional[str] = None)-> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query a region, based on SkyCoord and Angle objects, in the tess database and retrieve data in the chosen
        format.

        Filters can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        :param sky_coord: Sky coordinates object from the astropy module
        :type sky_coord: SkyCoord
        :param angle: Angle object from the astropy module
        :type angle: Angle
        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :param catalog: Allows to search in a specific catalog instead of the tess observation database (can be ``'TIC'`` or ``'TOI'``)
        :type catalog: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict


        .. dropdown:: Finding observations using a cone search
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.tess import Tess
                from astropy.coordinates import SkyCoord, Angle
                sky, a = SkyCoord('13h50m24s', '-60d21m11s', frame='icrs'), Angle('0.005d')
                values = Tess.query_region(sky_coord=sky, angle=a)
                
        .. dropdown:: Finding targets in the TOI catalog using a cone search
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.tess import Tess
                from astropy.coordinates import SkyCoord, Angle
                sky, a = SkyCoord('13h50m24s', '-60d21m11s', frame='icrs'), Angle('0.005d')
                values = Tess.query_region(sky_coord=sky, angle=a, catalog='TOI')
        """

        coordinate_filter_dict = self.dace.transform_coordinates_to_dict(sky_coord, angle)
        filters_with_coordinates = {}
        if filters is not None:
            filters_with_coordinates.update(filters)
        filters_with_coordinates.update(coordinate_filter_dict)
        
        if catalog is not None:
            if 'TIC' in catalog.upper():
                return self.query_tic_catalog(limit=limit, filters=filters_with_coordinates, output_format=output_format)
            elif 'TOI' in catalog.upper():
                return self.query_toi_catalog(limit=limit, filters=filters_with_coordinates, output_format=output_format)
            else:
                raise ValueError("Catalog must be 'TIC' or 'TOI'")
        else:
            return self.query_database(limit=limit, filters=filters_with_coordinates, output_format=output_format)

    def get_flux(self,
                 target: str,
                 flux_type: Optional[dict] = "raw_flux",
                 output_format: Optional[str] = None) \
            -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Retrieve tess photometry data for a specified target in the chosen format.

        All available formats are defined in this section (see :doc:`output_format`).

        Avalable flux types are [ 'raw_flux', 'corr_flux' ].

        :param target: The target to retrieve data from. (usually a TIC or TOI id)
        :type target: str
        :param flux_type: The flux type to use
        :type flux_type: Optional[str]
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting flux data for a given target
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.tess import Tess
                target_to_search = 'TIC381400181'
                values = Tess.get_flux(target=target_to_search)
        """
        options: dict = {
            "fluxType": flux_type,
            "computeModel": {
                "frequency": 48
            },
            "model": {
                "keplerians": {},
                "star": {
                    "RHO_RHOSUN": 1,
                    "LIMBDARK": "quadratic",
                    "LIMBDARKU0": 0.1,
                    "LIMBDARKU1": 0.3
                },
                "offsets": {}
            }

        }
        res = self.dace.request_post(
            api_name=self.__TESS_API,
            endpoint=f'flux/{target}',
            json_data=json.loads(json.dumps(options))
        )
        formatted_res = {}
        for key in res:
            formatted_res[key] = self.dace.transform_to_format(res[key], output_format=output_format)

        return formatted_res


Tess: TessClass = TessClass()
"""
This is a singleton instance of the :class:`TessClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.tess import Tess
"""