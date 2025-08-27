import pandas as pd
import random
import uuid
from datetime import datetime, timedelta
import os

# ==============================
# PARAMETERS
# ==============================
NUM_USERS = 200
FOLLOW_RATIO = 5        # avg number of users each user follows
POST_PROBABILITY = 0.3  # ~30% of users post
MAX_POSTS_PER_USER = 4
TAG_LIST = ['travel','food','art','fitness','tech','music','fashion','nature']
CAPTIONS = [
    "Sunset vibes 🌅",
    "Coffee time ☕",
    "Life is beautiful ✨",
    "Workout done 💪",
    "Delicious food 🍕",
    "Exploring the city 🏙️",
    "Weekend mood 😎",
    "Nature walk 🌿",
    "Feeling grateful 🙏",
    "Music is life 🎵"
]
COMMENT_TEXTS = ["Nice!", "🔥", "Love this", "Cool", "👏"]

OUTPUT_DIR = "./synthetic_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================
# STEP 1: Generate Users
# ==============================
def random_date(days_back=365):
    return (datetime.now() - timedelta(days=random.randint(0, days_back))).date().isoformat()

first_names = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Jamie", "Morgan", "Riley", "Cameron", "Quinn"]
last_names = ["Smith", "Johnson", "Brown", "Lee", "Garcia", "Martinez", "Davis", "Clark", "Lewis", "Walker"]

users = []
for i in range(1, NUM_USERS + 1):
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    email = name.lower().replace(" ", ".") + "@gmail.com"
    users.append({
        "userId": i,
        "name": name,
        "email": email,
        "createdAt": random_date()
    })

users_df = pd.DataFrame(users)
users_df.to_csv(os.path.join(OUTPUT_DIR, "users_200.csv"), index=False)

# ==============================
# STEP 2: Generate Follows
# ==============================
follows = []
for follower_id in range(1, NUM_USERS + 1):
    followees = random.sample([u for u in range(1, NUM_USERS + 1) if u != follower_id], 
                              k=min(FOLLOW_RATIO, NUM_USERS - 1))
    for followee_id in followees:
        follows.append({
            "srcUserId": follower_id,
            "dstUserId": followee_id,
            "since": random_date()
        })

follows_df = pd.DataFrame(follows)
follows_df.to_csv(os.path.join(OUTPUT_DIR, "follows_200.csv"), index=False)

# ==============================
# STEP 3: Generate Posts
# ==============================
posts = []
for u in users:
    if random.random() < POST_PROBABILITY:
        num_posts = random.randint(1, MAX_POSTS_PER_USER)
        for _ in range(num_posts):
            posts.append({
                "postId": str(uuid.uuid4()),
                "userId": u["userId"],
                "createdAt": random_date(),
                "caption": random.choice(CAPTIONS),
                "mediaUrl": f"https://picsum.photos/600/600?random={random.randint(1,10000)}",
                "likeCount": 0,
                "commentCount": 0
            })

posts_df = pd.DataFrame(posts)
posts_df.to_csv(os.path.join(OUTPUT_DIR, "posts_200.csv"), index=False)

# ==============================
# STEP 4: Tags
# ==============================
tags_df = pd.DataFrame(TAG_LIST, columns=["name"])
tags_df.to_csv(os.path.join(OUTPUT_DIR, "tags.csv"), index=False)

# ==============================
# STEP 5: Post-Tag relationships
# ==============================
post_tags = []
for _, p in posts_df.iterrows():
    num_tags = random.randint(1, 2)
    chosen_tags = random.sample(TAG_LIST, num_tags)
    for t in chosen_tags:
        post_tags.append({"postId": p["postId"], "tag": t})

post_tags_df = pd.DataFrame(post_tags)
post_tags_df.to_csv(os.path.join(OUTPUT_DIR, "post_tags.csv"), index=False)

# ==============================
# STEP 6: Likes
# ==============================
likes = []
for _, rel in follows_df.iterrows():
    follower = rel["srcUserId"]
    followee = rel["dstUserId"]
    user_posts = posts_df[posts_df["userId"] == followee]
    for _, p in user_posts.iterrows():
        if random.random() < 0.2:  # 20% chance to like
            likes.append({"userId": follower, "postId": p["postId"]})

likes_df = pd.DataFrame(likes)
# Update like counts
like_counts = likes_df.groupby("postId").size().to_dict()
posts_df["likeCount"] = posts_df["postId"].map(like_counts).fillna(0).astype(int)
likes_df.to_csv(os.path.join(OUTPUT_DIR, "likes.csv"), index=False)

# ==============================
# STEP 7: Comments
# ==============================
comments = []
for _, l in likes_df.iterrows():
    if random.random() < 0.1:  # 10% chance of comment
        comments.append({
            "commentId": str(uuid.uuid4()),
            "userId": l["userId"],
            "postId": l["postId"],
            "createdAt": datetime.now().isoformat(),
            "text": random.choice(COMMENT_TEXTS)
        })

comments_df = pd.DataFrame(comments)
# Update comment counts
comment_counts = comments_df.groupby("postId").size().to_dict()
posts_df["commentCount"] = posts_df["postId"].map(comment_counts).fillna(0).astype(int)
comments_df.to_csv(os.path.join(OUTPUT_DIR, "comments.csv"), index=False)

# Save updated posts with like/comment counts
posts_df.to_csv(os.path.join(OUTPUT_DIR, "posts_200.csv"), index=False)

print(f"✅ All synthetic CSVs created in {OUTPUT_DIR}")
