from pandas import DataFrame
from jobspy import scrape_jobs

from src.domain.contracts.extractor import BaseExtractor


class JobsApiExtractor(BaseExtractor):
    def __init__(self, search_term: str, location: str, results_wanted: int):
        self.search_term = search_term
        self.location = location
        self.results_wanted = results_wanted

    def extract(self) -> DataFrame:
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=self.search_term,
            location=self.location,
            results_wanted=self.results_wanted,
        )
        return jobs
