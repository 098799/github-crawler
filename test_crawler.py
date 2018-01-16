"""
### Usage: 
* If `pytest` variable is disabled, `python3 crawler.py input.json` creates `results.json`.
* With `pytest` enabled, input is read from the program file. 

### Notable libraries:
* requests: way more convenient than standard urllib.
* bs4: convenience. Could be done without it, but code would be less readable. 
"""
import requests
import json
from sys import argv
from random import choice
from bs4 import BeautifulSoup
from pytest import raises

def has_href_and_title(tag):
    """
    Search for element with attribute "href" and "title".
    """
    return tag.has_attr('href') and tag.has_attr('title')

    
def has_href_and_class(tag):
    """
    Search for element with attribute "href" and "class".
    """
    return tag.has_attr('href') and tag.has_attr('class')


def findLinks(htmlFile, webType, extras):
    """
    Input: soup object and str with search type.
    Output: list with appropriate links.
    """
    github = "https://github.com"
        
    divTypes = {"Repositories": "repo-list-item", "Issues": "issue-list-item",
                "Wikis": "wiki-list-item"} # different div for different search
    preList = htmlFile.find_all("div", {"class": divTypes[webType]})
    listOfLinks = []
    if webType == "Repositories": #links of interest in repos are different
        for item in preList:
            listOfLinks.append(item.find(has_href_and_class))
    elif webType == "Issues" or webType == "Wikis":
        for item in preList:
            listOfLinks.append(item.find(has_href_and_title))
    else:
        raise Exception("Not supported type of search.")
    
    # preparation of results
    results = []
    for link in listOfLinks:
        dictRes = {}
        dictRes["url"] = github + link["href"]
        if webType == "Repositories" and extras: #only for extra assignment
            dictRes["extra"] = {}
            dictRes["extra"]["owner"] = link["href"].split("/")[1]
        results.append(dictRes)
        
    return results


def findLanguages(htmlFile):
    """
    Input: soup object
    Output: list of lists with languages and percentages
    """
    languages = []
    preList = htmlFile.find_all("div", {"class": "repository-lang-stats-graph"})
    for item in preList:
        for spanItem in item.find_all("span"):
            languages.append(spanItem["aria-label"][:-1].split(" "))
    return languages


def parseGithub(inputData, extras):
    """
    Input: dict with provided data.
    Output: list with dicts of each of the search results.
    """
    github = "https://github.com"

    # Preparation of search data
    requestsData = {}
    requestsData["q"] = '+'.join(inputData["keywords"])
    requestsData["type"] = inputData["type"]
    requestsData["utf8"] = "✓"

    # http request with proxy
    proxies = {'http': 'http://' + choice(inputData["proxies"])}
    page = requests.get(github + "/search", params=requestsData, proxies=proxies)
    soupedPage = BeautifulSoup(page.text, 'html.parser')

    # parsing for lines with appropriate data
    results = findLinks(soupedPage, inputData["type"], extras)

    # extra assignment requests and preparation
    if inputData["type"] == "Repositories" and extras:
        for result in results:
            page = requests.get(result["url"], proxies=proxies)
            soupedPage = BeautifulSoup(page.text, 'html.parser')
            languages = findLanguages(soupedPage)
            result["extra"]["language_stats"] = {}
            for language in languages:
                result["extra"]["language_stats"][language[0]] = language[1]
    return results

def main():
    """
    Main function.
    """
    pytest = True
    # Input -- either fixed (for pytest) or standard
    if pytest:
        inputData = {
            "keywords": [
                "openstack",
                "nova",
                "css"
            ],
            "proxies": [
                "194.126.37.94:8080",
                "13.78.125.167:8080"
            ],
            "type": "Repositories"
        }
    else:
        with open(argv[1],'r') as infile:
            inputData = json.load(infile)
            
    extras = True   # True for enabling extra information (additional assignment)
    res = parseGithub(inputData, extras) # main subroutine

    # Output
    with open("results.json",'w') as outfile: 
        json.dump(res, outfile, indent=2)


if __name__ == "__main__":
    main()


# Testing arena
def test_has_href_and_title():
    assert has_href_and_title(BeautifulSoup("<a href='' title=''></a>", 'html.parser').a)
    
def test_has_href_and_class():
    assert has_href_and_class(BeautifulSoup("<a href='' class=''></a>", 'html.parser').a)
    
def test_findLinksRepo():
    """
    Real-life html excerpt from Github for subroutine testing
    """
    htmlFile = """
    <div class="repo-list-item d-flex flex-justify-start py-4 public source">
    <div class="col-8 pr-3">
    <h3>
    <a href="/atuldjadhav/DropBox-Cloud-Storage" class="v-align-middle">atuldjadhav/DropBox-Cloud-Storage</a>
    </h3>
    <p class="col-9 d-inline-block text-gray mb-2 pr-4">
    Technologies:- <em>Openstack</em> <em>NOVA</em>, NEUTRON, SWIFT, CINDER API's, JAVA, JAX-RS, MAVEN, JSON, HTML5, <em>CSS</em>, JAVASCRIPT, ANGUL…
    </p>
    <div class="d-flex">
    <p class="f6 text-gray mr-3 mb-0 mt-2">
    Updated <relative-time datetime="2016-03-29T19:40:33Z">Mar 29, 2016</relative-time>
    </p>
    </div>
    </div>
    <div class="d-table-cell col-2 text-gray pt-2">
    <span class="repo-language-color ml-0" style="background-color:#563d7c;"></span>
    CSS
    </div>
    </div>
    """
    expectedResult = [{'extra': {'owner': 'atuldjadhav'}, 'url': 'https://github.com/atuldjadhav/DropBox-Cloud-Storage'}]
    assert findLinks(BeautifulSoup(htmlFile, 'html.parser'), "Repositories", True) == expectedResult
    
def test_findLinksException():
    """
    Testing for exception
    """
    htmlFile = """
    <div class="repo-list-item d-flex flex-justify-start py-4 public source">
    """
    with raises(Exception, message="Not supported type of search."):
        findLinks(BeautifulSoup(htmlFile, 'html.parser'), "Repos", True) == expectedResult

def test_findLanguages():
    """
    Real-life html excerpt from Github for subroutine testing
    """
    htmlFile = """
    <div class="repository-lang-stats-graph js-toggle-lang-stats" title="Click for language details" data-ga-click="Repository, language bar stats toggle, location:repo overview">
      <span class="language-color" aria-label="CSS 52.0%" style="width:52.0%; background-color:#563d7c;" itemprop="keywords">CSS</span>
      <span class="language-color" aria-label="JavaScript 47.2%" style="width:47.2%; background-color:#f1e05a;" itemprop="keywords">JavaScript</span>
      <span class="language-color" aria-label="HTML 0.8%" style="width:0.8%; background-color:#e34c26;" itemprop="keywords">HTML</span>
    </div>
    """
    expectedResult = [['CSS', '52.0'], ['JavaScript', '47.2'], ['HTML', '0.8']]
    assert findLanguages(BeautifulSoup(htmlFile, 'html.parser')) == expectedResult

def test_parseGithub():
    inputData = {
        "keywords": [
            "openstack",
            "nova",
            "css"
        ],
        "proxies": [
            "194.126.37.94:8080",
            "13.78.125.167:8080"
        ],
        "type": "Repositories"
    }
    expectedResult = [{'extra': {'owner': 'atuldjadhav', 'language_stats': {'JavaScript': '47.2', 'HTML': '0.8', 'CSS': '52.0'}}, 'url': 'https://github.com/atuldjadhav/DropBox-Cloud-Storage'}]
    assert parseGithub(inputData,True) == expectedResult
    
def test_main():
    assert main() == None

def test_findLinksWiki():
    """
    Real-life html excerpt from Github for subroutine testing
    """
    htmlFile = """
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/vault-team"><img alt="@vault-team" class="avatar d-inline-block mr-2" height="32" src="https://avatars1.githubusercontent.com/u/23693611?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/vault-team/vault-website" class="h5">vault-team/vault-website</a>
        &#8211;
      <a href="/vault-team/vault-website/wiki/Quick-installation-guide" title="Quick installation guide">Quick installation guide</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2017-05-03T04:35:32Z">May 3, 2017</relative-time>.</div>
    </div>
  </div>
  <p>...  providers to access Vault API <em>Nova</em>: supports the deployment and management of virtual machines in the <em>OpenStack</em> cloud. A <em>Nova</em> instance is a virtual machine that runs inside <em>OpenStack</em> cloud Glance: manages ...</p>
</div>
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/iiwaziri"><img alt="@iiwaziri" class="avatar d-inline-block mr-2" height="32" src="https://avatars3.githubusercontent.com/u/9251936?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/iiwaziri/wiki_learn" class="h5">iiwaziri/wiki_learn</a>
        &#8211;
      <a href="/iiwaziri/wiki_learn/wiki/Packstack" title="Packstack">Packstack</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2018-01-02T04:18:01Z">Jan 2, 2018</relative-time>.</div>
    </div>
  </div>
  <p>... . Can be customized and rebranded by service providers and commercial vendors using custom .<em>css</em> files 3 dashboards: User dashboard System dashboard Settings dashboard <em>Nova</em> Provision and manage large ...</p>
</div>
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/marcosaletta"><img alt="@marcosaletta" class="avatar d-inline-block mr-2" height="32" src="https://avatars0.githubusercontent.com/u/9801368?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/marcosaletta/Juno-CentOS7-Guide" class="h5">marcosaletta/Juno-CentOS7-Guide</a>
        &#8211;
      <a href="/marcosaletta/Juno-CentOS7-Guide/wiki/2.-Controller-and-Network-Node-Installation" title="2. Controller and Network Node Installation">2. Controller and Network Node Installation</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2015-11-05T12:56:17Z">Nov 5, 2015</relative-time>.</div>
    </div>
  </div>
  <p>...  node. $ sudo yum install -y <em>openstack</em>-<em>nova</em>-api.noarch     
  $ sudo yum install -y <em>openstack</em>-<em>nova</em>-cert.noarch
  $ sudo yum install -y <em>openstack</em>-<em>nova</em>-conductor.noarch
  $ sudo yum install -y <em>openstack</em> ...</p>
</div>
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/MirantisDellCrowbar"><img alt="@MirantisDellCrowbar" class="avatar d-inline-block mr-2" height="32" src="https://avatars0.githubusercontent.com/u/1816130?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/MirantisDellCrowbar/crowbar" class="h5">MirantisDellCrowbar/crowbar</a>
        &#8211;
      <a href="/MirantisDellCrowbar/crowbar/wiki/Release-notes" title="Release notes">Release notes</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2012-11-08T17:25:35Z">Nov 8, 2012</relative-time>.</div>
    </div>
  </div>
  <p> deploy. Workaround:  Edit the barclamp and set the <em>Nova</em> - Volume to use Local.  ReApply. 900 <em>OpenStack</em> bonding network json doesn&#x27;t support multi-speed Crowbar allows down&#x2F;up-grading interface speeds</p>
</div>
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/dellcloudedge"><img alt="@dellcloudedge" class="avatar d-inline-block mr-2" height="32" src="https://avatars1.githubusercontent.com/u/724961?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/dellcloudedge/crowbar" class="h5">dellcloudedge/crowbar</a>
        &#8211;
      <a href="/dellcloudedge/crowbar/wiki/Release-notes" title="Release notes">Release notes</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2012-11-08T17:25:35Z">Nov 8, 2012</relative-time>.</div>
    </div>
  </div>
  <p> deploy. Workaround:  Edit the barclamp and set the <em>Nova</em> - Volume to use Local.  ReApply. 900 <em>OpenStack</em> bonding network json doesn&#x27;t support multi-speed Crowbar allows down&#x2F;up-grading interface speeds</p>
</div>
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/rhafer"><img alt="@rhafer" class="avatar d-inline-block mr-2" height="32" src="https://avatars0.githubusercontent.com/u/373399?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/rhafer/crowbar" class="h5">rhafer/crowbar</a>
        &#8211;
      <a href="/rhafer/crowbar/wiki/Release-notes" title="Release notes">Release notes</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2012-11-08T17:25:35Z">Nov 8, 2012</relative-time>.</div>
    </div>
  </div>
  <p> deploy. Workaround:  Edit the barclamp and set the <em>Nova</em> - Volume to use Local.  ReApply. 900 <em>OpenStack</em> bonding network json doesn&#x27;t support multi-speed Crowbar allows down&#x2F;up-grading interface speeds</p>
</div>
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/vinayakponangi"><img alt="@vinayakponangi" class="avatar d-inline-block mr-2" height="32" src="https://avatars2.githubusercontent.com/u/1770093?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/vinayakponangi/crowbar" class="h5">vinayakponangi/crowbar</a>
        &#8211;
      <a href="/vinayakponangi/crowbar/wiki/Release-notes" title="Release notes">Release notes</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2012-11-08T17:25:35Z">Nov 8, 2012</relative-time>.</div>
    </div>
  </div>
  <p> deploy. Workaround:  Edit the barclamp and set the <em>Nova</em> - Volume to use Local.  ReApply. 900 <em>OpenStack</em> bonding network json doesn&#x27;t support multi-speed Crowbar allows down&#x2F;up-grading interface speeds</p>
</div>
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/jamestyj"><img alt="@jamestyj" class="avatar d-inline-block mr-2" height="32" src="https://avatars0.githubusercontent.com/u/22206?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/jamestyj/crowbar" class="h5">jamestyj/crowbar</a>
        &#8211;
      <a href="/jamestyj/crowbar/wiki/Release-notes" title="Release notes">Release notes</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2012-11-08T17:25:35Z">Nov 8, 2012</relative-time>.</div>
    </div>
  </div>
  <p> deploy. Workaround:  Edit the barclamp and set the <em>Nova</em> - Volume to use Local.  ReApply. 900 <em>OpenStack</em> bonding network json doesn&#x27;t support multi-speed Crowbar allows down&#x2F;up-grading interface speeds</p>
</div>
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/eryeru12"><img alt="@eryeru12" class="avatar d-inline-block mr-2" height="32" src="https://avatars1.githubusercontent.com/u/7105573?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/eryeru12/crowbar" class="h5">eryeru12/crowbar</a>
        &#8211;
      <a href="/eryeru12/crowbar/wiki/Release-notes" title="Release notes">Release notes</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2012-11-08T17:25:35Z">Nov 8, 2012</relative-time>.</div>
    </div>
  </div>
  <p> deploy. Workaround:  Edit the barclamp and set the <em>Nova</em> - Volume to use Local.  ReApply. 900 <em>OpenStack</em> bonding network json doesn&#x27;t support multi-speed Crowbar allows down&#x2F;up-grading interface speeds</p>
</div>
<div class="wiki-list-item col-12 py-4 wiki-list-item-public ">
    <a href="/opencit"><img alt="@opencit" class="avatar d-inline-block mr-2" height="32" src="https://avatars0.githubusercontent.com/u/18556847?s=64&amp;v=4" width="32" /></a>
  <div class="d-inline-block">
    <div class="mb-2">
        <a href="/opencit/opencit" class="h5">opencit/opencit</a>
        &#8211;
      <a href="/opencit/opencit/wiki/Open-CIT-3.2-Product-Guide" title="Open CIT 3.2 Product Guide">Open CIT 3.2 Product Guide</a>
      <div class="f6 text-gray updated-at">Last updated <relative-time datetime="2017-09-07T16:42:28Z">Sep 7, 2017</relative-time>.</div>
    </div>
  </div>
  <p> to the appropriate <em>CSS</em> files relevant to the distribution&#x2F;version of <em>OpenStack</em> being used. 10.1.2 Instance View Changes File Changes and Other Notes distribution-location&#x2F;python2.7&#x2F;dist-packages&#x2F;<em>nova</em></p>
</div>
    """
    expectedResult = [{'url': 'https://github.com/vault-team/vault-website/wiki/Quick-installation-guide'}, {'url': 'https://github.com/iiwaziri/wiki_learn/wiki/Packstack'}, {'url': 'https://github.com/marcosaletta/Juno-CentOS7-Guide/wiki/2.-Controller-and-Network-Node-Installation'}, {'url': 'https://github.com/MirantisDellCrowbar/crowbar/wiki/Release-notes'}, {'url': 'https://github.com/dellcloudedge/crowbar/wiki/Release-notes'}, {'url': 'https://github.com/rhafer/crowbar/wiki/Release-notes'}, {'url': 'https://github.com/vinayakponangi/crowbar/wiki/Release-notes'}, {'url': 'https://github.com/jamestyj/crowbar/wiki/Release-notes'}, {'url': 'https://github.com/eryeru12/crowbar/wiki/Release-notes'}, {'url': 'https://github.com/opencit/opencit/wiki/Open-CIT-3.2-Product-Guide'}]
    assert findLinks(BeautifulSoup(htmlFile, 'html.parser'), "Wikis", True) == expectedResult
