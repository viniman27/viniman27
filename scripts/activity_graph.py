"""Generate the profile graph using GitHub data, with no hosted image service."""
import json
import os
from pathlib import Path
import urllib.request
from xml.sax.saxutils import escape


def render(days, username):
    days = sorted(days, key=lambda day: day['date'])[-31:]
    if len(days) != 31:
        raise ValueError('Expected at least 31 days of contribution data')
    counts = [int(day['contributionCount']) for day in days]
    maximum = max(max(counts), 1)
    points = [(60 + i * 28, 245 - count / maximum * 155)
              for i, count in enumerate(counts)]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 310" role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(username)} — Activity Graph</title>',
           f'<desc id="desc">{sum(counts)} contributions from {days[0]["date"]} to {days[-1]["date"]}. Daily GitHub contribution counts.</desc>',
           '<rect width="960" height="310" rx="12" fill="#0d1117"/>',
           '<g font-family="Arial, sans-serif" fill="#c9d1d9">',
           '<text x="60" y="38" font-size="22" fill="#3a9cdf">Contribution Activity</text>',
           f'<text x="60" y="62" font-size="13">{sum(counts)} contributions · last 31 days</text>']
    for fraction in (0, 0.5, 1):
        y = 245 - fraction * 155
        svg.append(f'<path d="M60 {y} H900" stroke="#30363d"/>')
        svg.append(f'<text x="45" y="{y + 4}" text-anchor="end" font-size="11">{maximum * fraction:g}</text>')
    coords = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
    svg.append(f'<polygon points="60,245 {coords} 900,245" fill="#3a9cdf" opacity="0.12"/>')
    svg.append(f'<polyline points="{coords}" fill="none" stroke="#3a9cdf" stroke-width="2.5"/>')
    for day, count, (x, y) in zip(days, counts, points):
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="#79c0ff"><title>{day["date"]}: {count} contributions</title></circle>')
    for i in (0, 5, 10, 15, 20, 25, 30):
        svg.append(f'<text x="{points[i][0]}" y="270" text-anchor="middle" font-size="11">{days[i]["date"][5:]}</text>')
    svg.append('</g></svg>\n')
    return '\n'.join(svg)


def main():
    username = os.environ.get('GRAPH_USERNAME', 'viniman27')
    query = 'query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}'
    request = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': {'login': username}}).encode(),
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Content-Type': 'application/json', 'User-Agent': 'profile-activity-graph'})
    with urllib.request.urlopen(request, timeout=45) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError(result['errors'])
    weeks = result['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    days = [day for week in weeks for day in week['contributionDays']]
    svg = render(days, username)
    output = Path('assets/activity-graph.svg')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding='utf-8')
    print(f'Generated {output} from {len(days)} real GitHub contribution days')


if __name__ == '__main__':
    main()
