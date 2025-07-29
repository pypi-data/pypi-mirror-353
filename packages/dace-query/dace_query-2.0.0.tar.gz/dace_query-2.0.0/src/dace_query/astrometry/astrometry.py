from __future__ import annotations

import json
import logging

# import re
from typing import Optional, Union

from astropy.table import Table
from astroquery.simbad import SimbadClass
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass

ASTROMETRY_DEFAULT_LIMIT = 10000


class AstrometryClass:
    """
    The astrometry class.
    Use to retrieve data from the astrometry module.


    .. tip::
    
        A catalog instance is already provided, to use it:

        .. code-block:: python

            from dace_query.astrometry import Astrometry

    """
    
    def __init__(self, dace_instance: Optional[DaceClass] = None):
        """
        Create a configurable astrometry object which uses a specified dace instance.

        :param dace_instance: A dace object
        :type dace_instance: Optional[DaceClass]

        .. code-block:: python

            from dace_query.astrometry import AstrometryClass
            astrometry_instance = AstrometryClass()

        """

        # Logging configuration
        self.__OBSERVATION_API = "obs-webapp"
        self.__ASTROMETRY_API = "astrom-webapp"

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"astrometry-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def _simbad_id_check(self, id):
        """
        Queries Simbad to retrieve either its HIP or Gaia DR3 id. It return the name of the catalog
        (HIP or GAIA DR3) and the id number of that catalog.
        If the input is a HIP id, it will return the same id.
        If the input is a Gaia DR3 id, it will return the same.

        It will always prefer the HIP id over the Gaia DR3 id. Meaning that if the input is from
        a different catalog, it will first search for a HIP id, if not available then it takes the
        Gaia DR3 id.

        :param id: The id to check
        :type id: str
        :return: catalog, id_number. The catalog name (HIP or GAIA DR3) and the id number.
        :rtype: (str, str)
        """
        # Validate the input type
        if not isinstance(id, str):
            raise TypeError("The identifier must be a string.")

        # Query SIMBAD
        custom_simbad = SimbadClass()
        result = custom_simbad.query_objectids(id)

        if result is None:
            raise ValueError(f"No object found for the given identifier: {id}")

        # Extract all identifiers
        all_ids = result["id"]

        # Check for HIP id
        hip_ids = [i for i in all_ids if i.startswith("HIP ")]
        if hip_ids:
            return "HIP", hip_ids[0].split()[1]

        # Check for Gaia DR3 id
        gaia_ids = [i for i in all_ids if i.startswith("Gaia DR3 ")]
        if gaia_ids:
            return "GAIA DR3", gaia_ids[0].split()[2]

        # If neither HIP nor Gaia DR3 id is found
        raise ValueError(
            f"No HIP or Gaia DR3 identifier found for the given object: {id}"
        )

    def query_hipparcos_database(self, id: str, output_format: str = None):
        """
        Query hipparcos database to retrieve data from the main hipparcos catalog with the
        basic information about a target and its solution.

        :param id: Target name or identifier
        :type id: str
        :param output_format: The desired format for the result data.
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Column descriptions
            :color: info
            :icon: list-unordered


            - ``hip`` (*-*): Hipparcos identifier.

            - ``mce`` (*-*): Main-catalogue entry.

            - ``nres`` (*-*): Number of residual records.

            - ``nc`` (*-*): Number of components.

            - ``isol_n`` (*-*): Solution type.

            - ``sce`` (*-*): Supplement-catalogue entry.

            - ``f2`` (*-*): Goodness of fit.

            - ``f1`` (*-*): Percentage of rejected observations.

            - ``hp`` (*mag*): Hp magnitude.

            - ``bmv`` (*mag*): B-V colour index.

            - ``varann`` (*-*): Reference to variability annex.

            - ``nob`` (*-*): Number of observations.

            - ``nr`` (*-*): Number of rejected observations.

            - ``radeg`` (*deg.*): Right Ascension.

            - ``dedeg`` (*deg.*): Declination.

            - ``plx`` (*mas*): Parallax.

            - ``pm_ra`` (*mas/yr*): Proper motion in Right Ascension.

            - ``pm_de`` (*mas/yr*): Proper motion in Declination.

            - ``e_ra`` (*mas*): Formal error on RAdeg.

            - ``e_de`` (*mas*): Formal error on DEdeg.

            - ``e_plx`` (*mas*): Formal error on Plx.

            - ``e_pmra`` (*mas/yr*): Formal error on pmRA.

            - ``e_pmde`` (*mas/yr*): Formal error on pmDE.

            - ``dpmra`` (*mas/yr²*): Acceleration in Right Ascension (7p, 9p).

            - ``dpmde`` (*mas/yr²*): Acceleration in Declination (7p, 9p).

            - ``e_dpmra`` (*mas/yr²*): Formal error on dpmRA (7p, 9p).

            - ``e_dpmde`` (*mas/yr²*): Formal error on dpmDE (7p, 9p).

            - ``ddpmra`` (*mas/yr³*): Acceleration change in Right Ascension (9p).

            - ``ddpmde`` (*mas/yr³*): Acceleration change in Declination (9p).

            - ``e_ddpmra`` (*mas/yr³*): Formal error on ddpmRA (9p).

            - ``e_ddpmde`` (*mas/yr³*): Formal error on ddpmDE (9p).

            - ``upsra`` (*mas*): VIM in Right Ascension (VIM).

            - ``upsde`` (*mas*): VIM in Declination (VIM).

            - ``e_upsra`` (*mas*): Formal error on upsRA (VIM).

            - ``e_upsde`` (*mas*): Formal error on upsDE (VIM).

            - ``var`` (*mas*): Cosmic dispersion added (stochastic).

            - ``gaia_gaiadr3_id`` (*-*): Gaia DR3 ID as matched by Gaia.

            - ``simbad_gaiadr3_id`` (*-*): Gaia DR3 ID as matched by SIMBAD.

            - ``gaiadr3_id_conflict`` (*-*): Indicates if there is a conflict in Gaia DR3 ID between sources.

            - ``iad_source`` (*-*): Indicates the source of the IAD, either "Brandt2021" or "JavaTool".


        .. dropdown:: Querying the Hipparcos database with a Hipparcos identifier
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace.astrometry import Astrometry
                Astrometry.query_hipparcos_database('HIP 1000', output_format='pandas')
                
                
        .. dropdown:: Querying the Hipparcos database with a Gaia DR3 identifier
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace.astrometry import Astrometry
                Astrometry.query_hipparcos_database('Gaia DR3 2361372542600289664', output_format='pandas')
        """
        # Query simbad to get the HIP or Gaia DR3 id
        catalog, id_number = self._simbad_id_check(id)

        # Query the backend
        if catalog == "HIP":
            backend_endpoint = f"hipparcos/model/hip/{id_number}"
        elif catalog == "GAIA DR3":
            backend_endpoint = f"hipparcos/model/gaia/{id_number}"

        return self.dace.transform_to_format(
            self.dace.request_get(
                self.__ASTROMETRY_API,
                backend_endpoint,
            ),
            output_format=output_format,
        )

    def get_hipparcos_timeseries(self, id: str, output_format: str = None):
        """
        Get the timeseries for a target from the Hipparcos Intermediate Astrometric Data (IAD).

        All available formats are defined in this section (see :doc:`output_format`).

        :param id: Target name or identifier
        :type id: str
        :param output_format: The desired format for the result data.
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Column descriptions
            :color: info
            :icon: list-unordered

            - ``IORB`` (*-*): Orbit number.

            - ``EPOCH`` (*years*): Observation epoch, given as Year - 1991.25.

            - ``PARF`` (*-*): Parallax factor.

            - ``CPSI`` (*-*): Cosine of Psi.

            - ``SPSI`` (*-*): Sine of Psi.

            - ``RES`` (*mas*): Abscissa residual.

            - ``SRES`` (*mas*): Formal error on abscissa residual.

            - ``HIP`` (*-*): Hipparcos identifier.

            - ``T_BJD`` (*days*): Epoch in Barycentric Julian Date (BJD).

            - ``S_MAS`` (*mas*): Absolute astrometric signal, RES + fitted model.

            - ``CTH`` (*-*): Cosine of the theta angle, following Gaia convention.

            - ``STH`` (*-*): Sine of the theta angle, following Gaia convention.

            - ``IAD_SOURCE`` (*-*): Indicates the source of the IAD, either "Brandt2021" or "JavaTool".


        .. dropdown:: Getting the hipparcos timeseries for a specific target
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace.astrometry import Astrometry
                Astrometry.get_hipparcos_timeseries("HIP 1000", output_format='pandas')
        """

        if id is None:
            raise ValueError("Please provide either a HIP id or a Gaia DR3 id.")

        if not isinstance(id, str):
            raise TypeError("The identifier must be a string.")

        # Query simbad to get the HIP or Gaia DR3 id
        catalog, id_number = self._simbad_id_check(id)

        # Query the backend
        if catalog == "HIP":
            backend_endpoint = f"hipparcos/iad/hip/{id_number}"
        elif catalog == "GAIA DR3":
            backend_endpoint = f"hipparcos/iad/gaia/{id_number}"

        return self.dace.transform_to_format(
            self.dace.request_get(
                self.__ASTROMETRY_API,
                backend_endpoint,
            ),
            output_format=output_format,
        )

    def query_database(
        self,
        limit: Optional[int] = ASTROMETRY_DEFAULT_LIMIT,
        filters: Optional[dict] = None,
        sort: Optional[dict] = None,
        output_format: Optional[str] = None,
    ) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the astrometry database to retrieve data in the chosen format.

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

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

        .. dropdown:: Getting the full astrometry database
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.astrometry import Astrometry
                values = Astrometry.query_database()
        """

        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__OBSERVATION_API,
                endpoint="observation/search/astrometry",
                params={
                    "limit": str(limit),
                    "filters": json.dumps(filters),
                    "sort": json.dumps(sort),
                },
            ),
            output_format=output_format,
        )

    def get_gaia_timeseries(
        self, target: str, output_format: Optional[str] = None
    ) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Get timeseries from Gaia astrometry for the specified target.

        All available formats are defined in this section (see :doc:`output_format`).

        :param target: The target name to retrieve astrometry data from
        :type target: str
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting Gaia timeseries for a specific target.
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.astrometry import Astrometry
                target_to_search = 'your-target'
                values = Astrometry.get_gaia_timeseries(target=target_to_search)
        """

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__OBSERVATION_API,
                endpoint=f"observation/astrometry/{target}",
            ),
            output_format=output_format,
        )


Astrometry: AstrometryClass = AstrometryClass()
"""
This is a singleton instance of the :class:`AstrometryClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.astrometry import Astrometry
"""
