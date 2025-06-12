from database import cursor, conn
from pulp import LpProblem, LpVariable, lpSum

VALO_RANK = {
    "Iron": 0,
    "Bronze": 1,
    "Silver": 2,
    "Gold": 3,
    "Platinum": 4,
    "Diamond": 5,
    "Ascendant": 6,
    "Immortal": 7,
    "Radiant": 8,
}

VALO_DIV = {
    "1": 0,
    "2": 1,
    "3": 2,
}

VALO_TEAM_SIZE = 5  # チームのサイズ

async def create(guild_id: int, users: list, team_num: int) -> dict:
    # ユーザー情報の取得
    placeholders = ','.join(['?'] * len(users))
    sql = f"SELECT user_id, rank, div FROM user_info WHERE guild_id = ? AND user_id IN ({placeholders})"
    cursor.execute(sql, (guild_id, *users))
    result = cursor.fetchall()
    if not result:
        raise ValueError("No users found in the database.")
    
    # ランク情報を数値に変換
    rank_score_users = dict()
    for user in result:
        user_id, rank, div = user
        if rank not in VALO_RANK:
            raise ValueError(f"Invalid rank '{rank}' for user {user_id}.")
        if str(div) not in VALO_DIV:
            raise ValueError(f"Invalid div '{div}' for user {user_id}.")
        rank_score_users[user_id] = VALO_RANK[rank] * len(VALO_DIV) + VALO_DIV[str(div)]
    print(f"Rank scores: {rank_score_users}")
    
    # チーム分け
    ## 問題の定義
    problem = LpProblem("TeamCreation")

    ## 変数の作成
    ### ユーザーリスト
    users = list(rank_score_users.keys())
    ### 各ユーザのチーム所属状況
    team_members = LpVariable.dicts("Team", (users, range(team_num)), cat="Binary")

    ## 目的関数の設定
    ### チームのランクスコアの差を最小化
    # チームスコア
    team_scores = [
        lpSum(team_members[user_id][i] * rank_score_users[user_id] for user_id in users)
        for i in range(team_num)
    ]

    # 絶対値最小化のための補助変数zを導入
    z = LpVariable("z", lowBound=0)
    problem += z, "MinimizeRankDifference"
    problem += team_scores[0] - team_scores[1] <= z
    problem += team_scores[1] - team_scores[0] <= z

    ## 制約条件の設定
    ### チームのサイズは5人
    for i in range(team_num):
        problem += (lpSum([team_members[user_id][i] for user_id in users]) == VALO_TEAM_SIZE), f"TeamSize_{i}"


    ### 各ユーザは最大1つのチームに所属
    for user_id in users:
        problem += (lpSum(team_members[user_id][i] for i in range(team_num)) <= 1), f"UserTeam_{user_id}"
    problem.solve()

    return {
        "team1": [user_id for user_id in users if team_members[user_id][0].varValue == 1],
        "team2": [user_id for user_id in users if team_members[user_id][1].varValue == 1]
    }

__all__ = ["create"]