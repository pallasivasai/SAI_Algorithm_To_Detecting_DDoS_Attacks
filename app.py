import requests

# Keep the complete research dashboard from the last full-featured commit.
# The bootstrap only patches dataset selection/loading; all dashboard features
# and the original UI remain in the pinned full-featured source.
BASE = "https://raw.githubusercontent.com/pallasivasai/SAI_Algorithm_To_Detecting_DDoS_Attacks/7fc4739ff4ef7d34503c9e0ee914372afcfd23d3/app.py"

response = requests.get(BASE, timeout=60)
response.raise_for_status()
source = response.text

# Real committed dataset only.
source = source.replace(
    'GITHUB_BRANCH = "main"\n',
    'GITHUB_BRANCH = "main"\n\nGITHUB_PRIMARY_CSV = "1. APA-DDoS-Dataset.csv"\n',
    1,
)

# GitHub tree discovery must never hide the real CSV.
source = source.replace(
    '        if response.status_code != 200:\n\n            return []',
    '        if response.status_code != 200:\n\n            return [GITHUB_PRIMARY_CSV]',
    1,
)
source = source.replace(
    '    except Exception:\n\n        return []',
    '    except Exception:\n\n        return [GITHUB_PRIMARY_CSV]',
    1,
)

# The filename contains spaces, so encode it for the raw GitHub URL.
source = source.replace(
    '    url = (\n        GITHUB_RAW_BASE\n        + path\n    )',
    '    from urllib.parse import quote\n\n    url = (\n        GITHUB_RAW_BASE\n        + quote(path, safe="/")\n    )',
    1,
)

# Always prefer the real APA dataset.
source = source.replace(
    '    selected = choose_best_csv(\n        csv_files\n    )',
    '    selected = GITHUB_PRIMARY_CSV',
    1,
)

# Never silently switch to Sample/Demo data.
old = '''if github_df is not None:\n\n    df = github_df.copy()\n\n    dataset_source = github_path\n\n    using_demo = False\n\nelse:\n\n    df = create_demo_dataset()\n\n    dataset_source = "Demo Dataset"\n\n    using_demo = True'''
new = '''if github_df is None:\n\n    st.error(\n        "APA DDoS Dataset could not be loaded from GitHub. "\n        "Sample/Demo data is disabled for this dashboard."\n    )\n    st.stop()\n\ndf = github_df.copy()\ndataset_source = github_path or GITHUB_PRIMARY_CSV\nusing_demo = False'''
source = source.replace(old, new, 1)

# Only the real APA DDoS dataset appears in the dashboard dropdown.
start = source.find('    dataset_options = [')
end = source.find('    dataset_choice = st.selectbox(', start)
if start != -1 and end != -1:
    source = source[:start] + '    dataset_options = [GITHUB_PRIMARY_CSV]\n\n' + source[end:]

exec(compile(source, BASE, "exec"), globals(), globals())
