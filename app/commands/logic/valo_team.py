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

async def create(user_info: list, team_num: int = 2) -> dict:
    # ユーザー情報の検証
    if not isinstance(user_info, list) or not all(isinstance(info, tuple) and len(info) == 3 for info in user_info):
        raise TypeError("user_infoは(user_id, rank, div)のタプルからなるリストである必要があります。")
    if not isinstance(team_num, int) or team_num <= 0:
        raise TypeError("team_numは正の整数である必要があります。")
    if team_num < 2:
        raise ValueError("チーム数は2以上である必要があります。")
    if len(user_info) < team_num * VALO_TEAM_SIZE:
        raise ValueError(f"ユーザー数が不足しています。必要: {team_num * VALO_TEAM_SIZE}人, 現在: {len(user_info)}人")
    
    # ランク情報を数値に変換
    rank_score_users = dict()
    for info in user_info:
        user_id, rank, div = info
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
    z_max = LpVariable("z_max", lowBound=0)
    z_min = LpVariable("z_min", lowBound=0)
    problem += z_max - z_min, "MinimizeRankDifference"
    for i in range(team_num):
        problem += team_scores[i] <= z_max
        problem += team_scores[i] >= z_min

    ## 制約条件の設定
    ### チームのサイズは5人
    for i in range(team_num):
        problem += (lpSum([team_members[user_id][i] for user_id in users]) == VALO_TEAM_SIZE), f"TeamSize_{i}"


    ### 各ユーザは最大1つのチームに所属
    for user_id in users:
        problem += (lpSum(team_members[user_id][i] for i in range(team_num)) <= 1), f"UserTeam_{user_id}"
    problem.solve()

    return {
        f"team{i+1}": [user_id for user_id in users if team_members[user_id][i].varValue == 1]
        for i in range(team_num)
    }

__all__ = ["create"]