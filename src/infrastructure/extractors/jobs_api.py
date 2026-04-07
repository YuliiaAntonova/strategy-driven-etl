"""Infrastructure extractor that fetches job postings from the JobSpy API.

This extractor is intentionally thin: it translates our configuration into a
`jobspy.scrape_jobs(...)` call and returns the resulting pandas DataFrame.
"""

from pandas import DataFrame
from jobspy import scrape_jobs

from src.domain.contracts.extractor import BaseExtractor


class JobsApiExtractor(BaseExtractor):
    """Extract jobs into a DataFrame using JobSpy.

    Parameters
    ----------
    search_term:
        Search query.
    location:
        Location filter.
    results_wanted:
        Target number of results to fetch.
    """

    def __init__(self, search_term: str, location: str, results_wanted: int):
        self.search_term = search_term
        self.location = location
        self.results_wanted = results_wanted

    def extract(self) -> DataFrame:
        if not self.search_term:
            raise ValueError("search_term must be a non-empty string")

        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=self.search_term,
            location=self.location,
            results_wanted=self.results_wanted,
        )
        return jobs
