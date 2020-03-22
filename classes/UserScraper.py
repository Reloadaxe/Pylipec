"""
A class to define the methods to scrape LinkedIn user-profile webpages

"""
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from utils import scroll_profile_page, get_entity
from time import sleep
from bs4 import BeautifulSoup as bs

class UserScraper(object):
    def __init__(self, driver):
        self.driver = driver

    def get_principal_informations(self, soup):
        principal_infos = get_entity("principal_informations")
        image_tag = soup.find(class_="presence-entity pv-top-card__image presence-entity--size-9 ember-view").find("img")
        if image_tag:
            principal_infos["imageUrl"] = image_tag['src']
        name_tag = soup.find(class_="pv-top-card--list").find("li")
        if name_tag:
            principal_infos["name"] = name_tag.get_text(strip=True)
        job_title_tag = soup.find("h2", class_="mt1 t-18 t-black t-normal")
        if job_title_tag:
            principal_infos["job_title"] = job_title_tag.get_text(strip=True)
        location_and_relation_tag = soup.find(class_="pv-top-card--list pv-top-card--list-bullet mt1")
        if location_and_relation_tag:
            location_tag = location_and_relation_tag.find("li")
            if location_tag:
                principal_infos["location"] = location_tag.get_text(strip=True)
            relation_tag = location_and_relation_tag.find_all("li")[1]
            if relation_tag:
                principal_infos["relations_number"] = relation_tag.get_text(strip=True).replace(" relations", '')
        return principal_infos
    
    def get_principal_skills(self, section):
        skills_p = []
        skills_p_list = section.find_all(class_="pv-skill-category-entity__top-skill pv-skill-category-entity pb3 pt4 pv-skill-endorsedSkill-entity relative ember-view")
        for skill_p_tag in skills_p_list:
            skill = get_entity("skill")
            name_tag = skill_p_tag.find(class_="pv-skill-category-entity__name-text t-16 t-black t-bold")
            if name_tag:
                skill["name"] = name_tag.get_text(strip=True)
            try:
                endorsements_number_tag = skill_p_tag.find(class_="pv-skill-category-entity__endorsement-count t-14 t-black--light t-normal")
                skill["endorsements_number"] = int(endorsements_number_tag.get_text(strip=True))
            except:
                pass
            verified_by_linkedin_tag = skill_p_tag.find(class_="pv-skill-entity__verified-icon m1 ivm-image-view-model ember-view")
            if verified_by_linkedin_tag:
                skill["verified_by_linkedin"] = True
            skills_p.append(skill)
        return skills_p
    
    def get_secondary_skills(self, section):
        skills_s = []
        skill_domain_tags = section.find_all(class_="pv-skill-category-list pv-profile-section__section-info mb6 ember-view")
        for skill_domain_tag in skill_domain_tags:
            domain_tag = skill_domain_tag.find(class_="pb2 t-16 t-black--light t-normal pv-skill-categories-section__secondary-skill-heading")
            domain = domain_tag.get_text(strip=True) if domain_tag else ""
            skills_s_list = skill_domain_tag.find_all("li")
            for skill_s_tag in skills_s_list:
                skill = get_entity("skill")
                skill["domain"] = domain
                name_tag = skill_s_tag.find(class_="pv-skill-category-entity__name-text t-16 t-black t-bold")
                if name_tag:
                    skill["name"] = name_tag.get_text(strip=True)
                try:
                    endorsements_number_tag = skill_s_tag.find(class_="pv-skill-category-entity__endorsement-count t-14 t-black--light t-normal")
                    skill["endorsements_number"] = int(endorsements_number_tag.get_text(strip=True))
                except:
                    pass
                verified_by_linkedin_tag = skill_s_tag.find(class_="pv-skill-entity__verified-icon m1 ivm-image-view-model ember-view")
                skill["verified_by_linkedin"] = True if verified_by_linkedin_tag else False
                skills_s.append(skill)
        return skills_s

    def get_skills(self, soup):
        skills = {"principal": [], "secondary": []}
        skill_section = soup.find(class_="pv-profile-section pv-skill-categories-section artdeco-container-card ember-view")
        if skill_section:
            skills["principal"] = self.get_principal_skills(skill_section.find("ol"))
            skills["secondary"] = self.get_secondary_skills(skill_section.find(id="skill-categories-expanded"))
        return skills

    def get_formations(self, soup):
        formations = []
        try:
            formations_tag_list = soup.find(class_="pv-profile-section education-section ember-view").find(class_="pv-profile-section__section-info section-info pv-profile-section__section-info--has-more").find_all("li")
        except:
            try:
                formations_tag_list = soup.find(class_="pv-profile-section education-section ember-view").find(class_="pv-profile-section__section-info section-info pv-profile-section__section-info--has-no-more").find_all("li")
            except:
                formations_tag_list = None
        if formations_tag_list:
            for formation_tag in formations_tag_list:
                formation = get_entity("formation")
                image_tag = formation_tag.find("img")
                if image_tag:
                    formation["school"]["imageUrl"] = image_tag['src']
                title_tag = formation_tag.find(class_="pv-entity__school-name t-16 t-black t-bold")
                if title_tag:
                    formation["school"]["title"] = title_tag.get_text(strip=True)
                degree_tag = formation_tag.find(class_="pv-entity__comma-item")
                if degree_tag:
                    formation["degree"] = degree_tag.get_text(strip=True)
                try:
                    domain_tag = formation_tag.find(class_="pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal").find(class_="pv-entity__comma-item")
                    formation["domain"] = domain_tag.get_text(strip=True)
                except:
                    pass
                description_tag = formation_tag.find(class_="pv-entity__description t-14 t-normal mt4")
                if description_tag:
                    formation["description"] = description_tag.get_text(strip=True)
                times_tag = formation_tag.find_all("time")
                if len(times_tag) > 0:
                    formation["begin"] = times_tag[0].get_text(strip=True)
                if len(times_tag) > 1:
                    formation["end"] = times_tag[1].get_text(strip=True)
                formations.append(formation)
        return formations

    def get_experiences(self, soup):
        experiences = []
        try:
            experiences_tag_list = soup.find(class_="pv-profile-section experience-section ember-view").find(class_="pv-profile-section__section-info section-info pv-profile-section__section-info--has-more").find_all("li")
        except:
            try:
                experiences_tag_list = soup.find(class_="pv-profile-section experience-section ember-view").find(class_="pv-profile-section__section-info section-info pv-profile-section__section-info--has-no-more").find_all("li")
            except:
                experiences_tag_list = None
        if experiences_tag_list:
            for experience_tag in experiences_tag_list:
                experience = get_entity("experience")
                image_tag = experience_tag.find("img")
                if image_tag:
                    experience["corporation"]["imageUrl"] = image_tag['src']
                job_title_tag = experience_tag.find(class_="t-16 t-black t-bold")
                if job_title_tag:
                    experience["job_title"] = job_title_tag.get_text(strip=True)
                contract_tag = experience_tag.find(class_="pv-entity__secondary-title separator")
                if contract_tag:
                    experience["contract"] = contract_tag.get_text(strip=True)
                corpname_tag = experience_tag.find(class_="pv-entity__secondary-title t-14 t-black t-normal")
                if corpname_tag:
                    experience["corporation"]["title"] = corpname_tag.get_text(strip=True).replace(experience["contract"], '')
                try:
                    location_tag = soup.find(class_="pv-entity__location t-14 t-black--light t-normal block").find_all("span")[1]
                    experience["location"] = location_tag.get_text(strip=True)
                except:
                    pass
                try:
                    range_date_tag = experience_tag.find(class_="pv-entity__date-range t-14 t-black--light t-normal").find_all("span")[1]
                    dates = range_date_tag.get_text(strip=True).split('–')
                    experience["begin"] = dates[0].strip()
                    experience["end"] = dates[1].strip()
                except:
                    pass
                duration_tag = experience_tag.find(class_="pv-entity__bullet-item-v2")
                if duration_tag:
                    experience["duration"] = duration_tag.get_text(strip=True)
                experiences.append(experience)
        return experiences

    def get_languages(self, soup):
        languages = []
        accomplishment_tags = soup.find_all(
            class_="pv-accomplishments-block__list-container")
        for a in accomplishment_tags:
            try:
                if a["id"] == "languages-expandable-content":
                    languages = [l.get_text() for l in a.find_all("li")]
            except KeyError:
                pass
        return languages

    def scrape_user(self, query, url):
        attempt = 0
        max_attempts = 3
        success = False
        user_data = {}
        while not success:
            try:
                attempt += 1
                self.driver.get(url)
                sleep(2)
                self.driver.execute_script(
                    "document.body.style.zoom='50%'")
                sleep(2)
                scroll_profile_page(self.driver)
                try:
                    sleep(2)
                    show_more_skills = self.driver.find_element_by_class_name('pv-skills-section__additional-skills')
                    sleep(0.5)
                except:
                    show_more_skills = None
                if show_more_skills:
                    self.driver.execute_script("arguments[0].click();", show_more_skills)
                sleep(2)
                try:
                    show_more_button = self.driver.find_element_by_css_selector(".pv-profile-section__see-more-inline.pv-profile-section__text-truncate-toggle.link.link-without-hover-state")
                except:
                    show_more_button = None
                while show_more_button:
                    sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", show_more_button)
                    sleep(2)
                    try:
                        show_more_button = self.driver.find_element_by_css_selector(".pv-profile-section__see-more-inline.pv-profile-section__text-truncate-toggle.link.link-without-hover-state")
                    except:
                        show_more_button = None
                soup = bs(self.driver.page_source, 'html.parser')
                skills = self.get_skills(soup)
                principal_informations = self.get_principal_informations(soup)
                formations = self.get_formations(soup)
                languages = self.get_languages(soup)
                experiences = self.get_experiences(soup)
                user_data = {
                    "URL": url,
                    "query": query,
                    "principal_informations": principal_informations,
                    "formations": formations,
                    "languages": languages,
                    "experiences": experiences,
                    "skills": skills
                }
                success = True
            except TimeoutException:
                print("\nINFO :: TimeoutException raised while " +
                      "getting URL\n" + url)
                print("INFO :: Attempt n." + str(attempt) + " of " +
                      str(max_attempts) +
                      "\nNext attempt in 60 seconds")
                sleep(60)
            if success:
                break
            if attempt == max_attempts and not user_data:
                print("INFO :: Max number of attempts reached. " +
                      "Skipping URL" +
                      "\nUser data will be empty.")
        return user_data
