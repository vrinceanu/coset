# This script connects to the COSET database and extracts information about people and their associated metadata, including categories and photos. The extracted data is then saved as a pickle file for later use.
# fields to map information to:
# last_first,  name, active, classification, department,
# rank, admin_role, room, email, phone
# cv_link, photo_link, biography
#
#

import pymysql, json
import urllib.request

conn = pymysql.connect(
    host='coset.tsu.edu',
    user='vrinceanu',
    password='12AtlBos34',
    database='coset_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

print("fetching categories")
terms = 46*["none"]
with conn.cursor() as cursor:
    sql = "select term_id, slug from db_terms"
    cursor.execute(sql)
    records = cursor.fetchall()
    for rec in records:
        terms[rec['term_id']] = rec['slug']
print(terms)

dept_map = {
    'aerospace-and-mechanical-engineering': 'ASME',
    'biology': 'BIOL',
    'chemical-engineering-and-environmental-toxicology': 'CEET',
    'civil-engineering-and-transportation-studies': 'CETS',
    'electrical-engineering-and-computer-science': 'EECS',
    'engineering': 'ENG',
    'eis': 'EIS',
    'mathematics': 'MATH',
    'physics': 'PHYS',
    'chemistry': 'CHEM',
    'computer-science': 'CS',
    'transportation': 'TS',
    'administration': 'ADMI'
    }

print("fetching people")
with conn.cursor() as cursor:
    sql = "select ID, post_title, post_name, post_excerpt, post_status, post_content from db_posts where post_type='people'"
    cursor.execute(sql)
    people_posts = cursor.fetchall()
    people = []
    for entry in people_posts:
        person = {}
        person['last_first'] = entry['post_title']
        person['name'] = entry['post_name']

        person['active'] = False
        if entry['post_status'] == 'publish':   
            person['active'] = True
        
        person['biography'] = entry['post_content']
        
        print("fetching metadata for " + entry['post_title'] + " with id " + str(entry['ID']))
        sql = "select meta_key, meta_value from db_postmeta where post_id="+str(entry['ID'])
        cursor.execute(sql)
        meta = cursor.fetchall()
        record = {}
        for rec in meta:
            record[rec['meta_key']] =  rec['meta_value']
        record['admin_role'] = record.get('admin',"")
        record['cv_link'] = record.get('CV_link',"")
        for item in ('name', 'rank','admin_role','room','email','phone','cv_link'):
            person[item] = record.get(item,'')
        
        sql = "select term_taxonomy_id from db_term_relationships where object_id="+str(entry['ID'])
        cursor.execute(sql)
        cats = [x['term_taxonomy_id'] for x in cursor.fetchall()]
        if 21 in cats:
            person['classification'] = 'faculty'
        elif 22 in cats:
            person['classification'] = 'staff'
        else:
            person['classification'] = ''
        
        homes = [terms[k] for k in cats if k >= 30 and k<= 39]
        if homes:
            person['department'] = dept_map[homes[0]]
        else:
            person['department']='unknown'

        if person['email']:
            person['slug'] = person['email'].split('@')[0].replace('.','-')
        else:
            last, first = person['last_first'].split(',')
            person['slug'] = first.casefold().strip() + "-" + last.casefold().strip()
                    
        person['photo'] = ''
        if '_thumbnail_id' in record:
            sql = "select meta_key, meta_value from db_postmeta where post_id="+ str(record['_thumbnail_id'])
            cursor.execute(sql)
            thumb = cursor.fetchone().get('meta_value','none')
            thumb = "http://coset.tsu.edu/wp-content/uploads/"+thumb
            person['photo'] = f"{person['slug']}.jpg"
            save_path = f"media/{person['photo']}"
            print(thumb)
            try:
                urllib.request.urlretrieve(thumb, save_path)
            except Exception as e:
                print(f"An error occurred: {e}")

        people.append(person)

with open('people.json','w') as file:
    json.dump(people,file,indent=4)

