import os
import glob

base_dir = r"E:\Paresh\Auto Post\Auto-Insta-Krishna\website\public\articles"
articles = [os.path.basename(f) for f in glob.glob(os.path.join(base_dir, "*.html"))]
print(f"Total articles found: {len(articles)}")

xml_entries = []
# Include the main articles.html page itself
xml_entries.append("""  <url>
    <loc>https://krishnavibez.in/articles.html</loc>
    <lastmod>2026-11-21</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")

for a in sorted(articles):
    xml_entries.append(f"""  <url>
    <loc>https://krishnavibez.in/articles/{a}</loc>
    <lastmod>2026-11-21</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""")

sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sitemap_xml += '\n'.join(xml_entries) + '\n'
sitemap_xml += '</urlset>\n'

path1 = r"E:\Paresh\Auto Post\Auto-Insta-Krishna\website\public\articles-sitemap.xml"
with open(path1, "w", encoding="utf-8") as f:
    f.write(sitemap_xml)
print(f"Written: {path1}")

path2 = r"E:\Paresh\Auto Post\Krishna Vibez\public\articles-sitemap.xml"
with open(path2, "w", encoding="utf-8") as f:
    f.write(sitemap_xml)
print(f"Written: {path2}")

