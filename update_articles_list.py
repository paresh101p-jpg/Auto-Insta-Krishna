import re

p = '/data/user/0/ai.antigem/files/home/projects/Auto-Insta-Krishna/website/public/articles.html'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

card = """
    <article class="article-card" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,215,0,0.15); border-radius: 12px; overflow: hidden; margin-bottom: 24px;">
      <div class="article-thumb-wrap">
        <a href="/articles/karmanye-vadhikaraste-mehnat-fal-krishna-gita-upay.html">
          <img src="/images/articles/karmanye-vadhikaraste-krishna-viral-hero.jpg" alt="कर्मण्येवाधिकारस्ते: जब मेहनत का फल न मिले तो श्रीकृष्ण की ये 3 बातें याद रखें - Krishna Vibez" style="width: 100%; height: auto; max-height: 240px; object-fit: cover; display: block;" loading="lazy" width="600" height="338">
        </a>
      </div>
      <div class="article-info" style="padding: 16px;">
        <span class="category-badge" style="background: rgba(255,215,0,0.15); color: #ffaa00; font-size: 0.8rem; padding: 3px 8px; border-radius: 4px; font-weight: 600;">कर्मयोग रहस्य</span>
        <h2 class="article-title" style="margin: 10px 0 8px;"><a href="/articles/karmanye-vadhikaraste-mehnat-fal-krishna-gita-upay.html" style="color: #fff; text-decoration: none; font-size: 1.25rem;">कर्मण्येवाधिकारस्ते: जब मेहनत का फल न मिले तो श्रीकृष्ण की ये 3 बातें याद रखें</a></h2>
        <p class="article-excerpt" style="color: rgba(255,255,255,0.7); font-size: 0.95rem; line-height: 1.5; margin-bottom: 14px;">क्या दिन-रात परिश्रम के बाद भी असफलता और निराशा मिल रही है? जानिए श्रीमद्भगवद्गीता के कर्मयोग का गुप्त रहस्य और भगवान श्रीकृष्ण की 3 दिव्य नीतियां।</p>
        <a href="/articles/karmanye-vadhikaraste-mehnat-fal-krishna-gita-upay.html" class="read-more-btn" style="background: #ffaa00; color: #000; font-weight: 700; text-decoration: none; padding: 6px 14px; border-radius: 6px; display: inline-block;">पूरा लेख पढ़ें ➔</a>
      </div>
    </article>
"""

target = '<div class="articles-grid"'
if target in text:
    parts = text.split(target, 1)
    idx = parts[1].find('>')
    new_text = parts[0] + target + parts[1][:idx+1] + '\n' + card + parts[1][idx+1:]
    with open(p, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('Inserted new article card at top of articles.html!')

# Update sitemap
sitemap_path = '/data/user/0/ai.antigem/files/home/projects/Auto-Insta-Krishna/website/public/articles-sitemap.xml'
with open(sitemap_path, 'r', encoding='utf-8') as f:
    s_text = f.read()

new_url_entry = """  <url>
    <loc>https://krishnavibez.in/articles/karmanye-vadhikaraste-mehnat-fal-krishna-gita-upay</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
"""
if '</urlset>' in s_text:
    s_text = s_text.replace('</urlset>', new_url_entry + '</urlset>')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(s_text)
    print('Updated sitemap!')
