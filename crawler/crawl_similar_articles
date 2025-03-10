import requests
from bs4 import BeautifulSoup
import os
import dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from lxml import etree
import re
from collections import Counter
from tqdm import tqdm
import xml.etree.ElementTree as ET
import logging
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv() 
openai_api_key = os.getenv('OPENAI_API_KEY')

model = ChatOpenAI(api_key=openai_api_key)

namespaces = {
    "paper1": ["../RAG-project/RAG-project/papers/paper1.pdf"],
    #"paper2": ["../RAG-project/papers/paper2.pdf"],
    #"paper3": ["../RAG-project/papers/paper3.pdf"]
}


def download_pdfs(path, doi_list):
    if not os.path.exists(path):
        os.makedirs(path)
    if isinstance(doi_list, str):
        doi_list = [doi_list]
    temp_list = []
    for doi in doi_list:
        url = f"https://sci-hub.se/{doi}"
        response = requests.get(url)
        # check the request whether sends successfully or not
        if response.status_code == 200:
            print(f"request {url} successfully")
        else:
            print(f"request {url} failed")  
            continue
    
    soup = BeautifulSoup(response.text, 'html.parser')
    buttons = soup.find_all('button', onclick=True)

    for button in buttons:
        onclick = button.get('onclick')
        if onclick:
            pdf_url = onclick.split("'")[1]
            temp_list.append((pdf_url, doi))
            print("pdf_url:", pdf_url)
        print("temp_list:", temp_list)
    
    for temp, doi in temp_list:
        pdf_url = f"https:{temp}"
        try:
            response = requests.get(pdf_url)
            if response.status_code == 200:
                filename = doi.replace("/", "_") + ".pdf"
                file_path = os.path.join(path, filename)
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"File downloaded and saved as: {file_path}")
            else: print(f"Download failed, Status Code: {response.status_code}, URL: {pdf_url}")
        except Exception as e:
            print(f"Download failed, Error: {e}, URL: {pdf_url}")

def clean_text(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[§†‡]', '', text)
    # Merge split words
    text = re.sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)
    return text.strip()


def extract_keywords_from_pdf(file_paths, model, max_keywords: int = 3) -> list:
    all_text_chunks = []
    all_keywords = []

    for file_path in file_paths:
        loader = PyPDFLoader(file_path=file_path)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )
        texts = text_splitter.split_documents(data)
        
        for t in texts:
            t.page_content = clean_text(t.page_content)

        all_text_chunks.extend(texts)
        print(f'Loaded {len(texts)} chunks from {file_path}')

        for chunk in texts:
            prompt = f"""
            You are a helpful assistant.
            Please read the following text and extract up to {max_keywords} keywords or key phrases 
            that best represent the content. 
            Output them as a comma-separated list.

            Text:
            {chunk.page_content}

            Keywords:
            """
            response = model.invoke(prompt)
            chunk_keywords = [
                kw.strip()
                for kw in response.content.split(",")
                if kw.strip()  
            ]
            all_keywords.extend(chunk_keywords)

    counter = Counter(all_keywords)
    most_common_pairs = counter.most_common(max_keywords)
    top_keywords = [kw for kw, _freq in most_common_pairs]

    return top_keywords




class ArticleRetrieval:
    def __init__(self,
                    keywords: list = [],
                    pmids: list = [],
                    repo_dir = 'repodir',
                    retmax = 500,
                    pmc_ids: list = [],
                    scihub_doi: list = [],
                    failed_pmids: list = []):
        if keywords is [] and pmids is []:
            raise ValueError("Either keywords or pmids must be provided.")
        
        self.keywords = keywords
        self.pmids = pmids
        self.repo_dir = repo_dir
        self.retmax = retmax
        self.pmc_ids = pmc_ids
        self.scihub_doi = scihub_doi
        self.failed_pmids = failed_pmids


    
    def _get_all_text(self, element):
        if element is None:
            return ""
        
        text = element.text or ""
        for child in element:
            text += self._get_all_text(child)
            if child is not None and child.tail:
                text += child.tail
        return text

    def _clean_xml(self, txt):
        parser = etree.XMLParser(recover=True)
        root = ET.fromstring(txt, parser=parser)
        txt = self._get_all_text(root)
        txt = txt.split('REFERENCES')[0]
        text = '\n\n'.join([t.strip() for t in txt.split('\n') if len(t.strip())>250])
        return text
    
    def fetch_full_text(self):
        if not os.path.exists(self.repo_dir):
            os.makedirs(self.repo_dir, exist_ok=True)
        if not os.path.exists(self.repo_dir + '_ab'):
            os.makedirs(self.repo_dir + '_ab', exist_ok=True)

        print(f"Saving articles to {self.repo_dir}.")
        self.pmc_success = 0
        self.scihub_success = 0
        self.abstract_success = 0
        self.failed_download = []
        self.failed_abstract = []
        downloaded = os.listdir(self.repo_dir)
        downloaded_ab = os.listdir(self.repo_dir + '_ab')

        # 1) Fetching full text from PMC IDs
        for id in tqdm(self.pmc_ids, desc="Fetching full texts", unit="article"):
            if f"{id}.txt" in downloaded:
                print(f"File already downloaded: {id}")
                self.pmc_success += 1
                continue
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {
                "db": "pmc",
                "id": id,
                "rettype": "xml",
                "retmode": "text"
            }
            response = requests.get(base_url, params=params)
            full_text = self._clean_xml(response.text)
            if full_text.strip() == '':
                self.failed_download.append(id)
                continue
            else:
                logger.info(full_text[:200])
                with open(os.path.join(self.repo_dir, f'{id}.txt'), 'w', encoding='utf-8') as f:
                    f.write(full_text)
                self.pmc_success += 1

        # 2) Fetching PDFs from Sci-Hub DOIs
        for doi in tqdm(self.scihub_doi, desc="Fetching full texts", unit="article"):
            if f"{doi.replace('/','_')}.pdf" in downloaded: 
                print(f"File already downloaded: {doi}")
                self.scihub_success += 1
                continue

            if download_pdfs(path=self.repo_dir, doi_list=doi):
                self.scihub_success += 1
            else:
                self.failed_download.append(doi)

        # 3) Fetching abstracts from PubMed
        for pmid in tqdm(self.pmids, desc="Fetching abstract texts", unit="article"):
            if f"{pmid}.txt" in downloaded_ab:
                print(f"File already downloaded: {pmid}")
                self.scihub_success += 1
                continue
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": pmid,
            }

            response = requests.get(base_url, params=params)
            root = ET.fromstring(response.content)
            abstract = root.find('.//AbstractText')
            if abstract is not None:
                with open(os.path.join(self.repo_dir + '_ab', f'{pmid}.txt'), 'w', encoding='utf-8') as f:
                    f.write(abstract.text)
                self.abstract_success += 1
            else:
                self.failed_abstract.append(pmid)





def pmids_to_pmc_doi(pmids):
    if not pmids:
        return []

    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids)
    }
    resp = requests.get(summary_url, params=params)
    root = ET.fromstring(resp.content)

    results = []
    for docsum in root.findall('DocSum'):
        pmcid = None
        doi = None
        abstract = None
        id_value = docsum.find('Id').text
        for item in docsum.findall('.//Item[@Name="doi"]'):
            doi = item.text
            break
        for item in docsum.findall('.//Item[@Name="pmc"]'):
            pmcid = item.text
            break

        results.append((id_value, pmcid, doi))
    logger.info(f"total {len(results)} articles:")
    logger.info(f"found {len([r for r in results if r[1] is not None])} articles with PMC ID.")
    logger.info(f"found {len([r for r in results if r[2] is not None])} articles with DOI.")
    logger.info(f"found {len([r for r in results if r[1] is None and r[2] is None])} articles without PMC ID and DOI.")
    esummaries = results
    pmc_ids = [r[1] for r in results if r[1] is not None]
    scihub_doi = [r[2] for r in results if r[1] is None and r[2] is not None]
    failed_pmids = [r[0] for r in results if r[1] is None and r[2] is None]
    return pmc_ids, scihub_doi, failed_pmids


def search_pubmed_by_keywords(keywords, retmax=10):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": "+".join(keywords),
        "retmax": retmax
    }
    resp = requests.get(base_url, params=params)
    root = ET.fromstring(resp.content)
    idlist = root.find('.//IdList')
    pmids = []
    if idlist is not None:
        pmids = [elem.text for elem in idlist.findall('.//Id')]
    logger.info(f"Found {len(pmids)} PMIDs for keywords {keywords}.")
    return pmids


if __name__ == "__main__":
    if os.path.exists('repodir'):
        shutil.rmtree('repodir')
    if os.path.exists('repodir_ab'):
        shutil.rmtree('repodir_ab')

    for namespace, file_paths in namespaces.items():
        top_keywords = extract_keywords_from_pdf(file_paths, model, max_keywords=3)
        print("Top 3 keywords from local PDFs:", top_keywords)

        pmids = search_pubmed_by_keywords(top_keywords, retmax=5)
        print("PMIDs from PubMed:", pmids)

        pmc_ids, scihub_doi, failed_pmids = pmids_to_pmc_doi(pmids)

        articelfinder = ArticleRetrieval(keywords = top_keywords,
                                        pmids = pmids,
                                        repo_dir = 'repodir',
                                        retmax = 5,
                                        pmc_ids=pmc_ids,
                                        scihub_doi=scihub_doi,
                                        failed_pmids=failed_pmids)
        articelfinder.fetch_full_text()
