import flet as ft
import random

def main(page: ft.Page):
    page.title = "오징어 게임: 유리 징검다리"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = "auto"

    # 게임 데이터 저장소
    game_data = {
        "bridge": [],
        "current_step": 0,
        "players": [],
        "current_player_idx": 0,
        "survivors": [],
        "dead": []
    }

    # --- UI 요소 정의 ---
    status_text = ft.Text("설정을 완료하고 게임을 시작하세요.", size=18, color="yellow")
    log_list = ft.ListView(expand=True, spacing=5, height=200)
    
    # 1, 2번 조건: 인원수 및 다리 칸 수 입력
    player_count_ref = ft.TextField(label="참가 인원수", value="3", keyboard_type=ft.KeyboardType.NUMBER, width=150)
    bridge_len_ref = ft.TextField(label="다리 칸 수", value="5", keyboard_type=ft.KeyboardType.NUMBER, width=150)
    
    # 3번 조건: 이름 입력 칸들을 담을 컨테이너
    name_inputs_col = ft.Column()

    def create_name_fields(e):
        """인원수에 맞춰 이름 입력창 생성"""
        try:
            count = int(player_count_ref.value)
            name_inputs_col.controls = [ft.TextField(label=f"{i+1}번 참가자 이름", value=f"참가자{i+1}") for i in range(count)]
            setup_view.visible = False
            name_view.visible = True
            page.update()
        except:
            status_text.value = "⚠️ 인원수를 숫자로 입력해주세요."
            page.update()

    def start_game(e):
        """4번 조건: 이름 수집 및 랜덤 순서 결정 후 게임 시작"""
        game_data["players"] = [tf.value for tf in name_inputs_col.controls]
        random.shuffle(game_data["players"]) # 랜덤 순서 정하기
        
        b_len = int(bridge_len_ref.value)
        game_data["bridge"] = [random.choice(['L', 'R']) for _ in range(b_len)]
        game_data["current_step"] = 0
        game_data["current_player_idx"] = 0
        game_data["survivors"] = []
        game_data["dead"] = []
        
        log_list.controls.clear()
        name_view.visible = False
        game_view.visible = True
        update_game_ui(f"🎲 결정된 순서: {' -> '.join(game_data['players'])}")
        page.update()

    def update_game_ui(msg):
        status_text.value = msg
        step_info.value = f"현재 단계: {game_data['current_step'] + 1} / {len(game_data['bridge'])} 칸"
        player_info.value = f"현재 도전자: {game_data['players'][game_data['current_player_idx']]}"
        page.update()

    def handle_choice(e):
        choice = e.control.data
        player = game_data["players"][game_data["current_player_idx"]]
        
        if choice == game_data["bridge"][game_data["current_step"]]:
            log_list.controls.insert(0, ft.Text(f"✨ {player}: {game_data['current_step']+1}칸 통과!", color="green"))
            game_data["current_step"] += 1
        else:
            log_list.controls.insert(0, ft.Text(f"💀 {player}: {game_data['current_step']+1}칸에서 추락!", color="red"))
            game_data["dead"].append(player)
            game_data["current_player_idx"] += 1
            game_data["current_step"] += 1 

        # 게임 종료 체크
        if game_data["current_step"] >= len(game_data["bridge"]):
            finish_game()
        elif game_data["current_player_idx"] >= len(game_data["players"]):
            finish_game(all_dead=True)
        else:
            update_game_ui(f"다음 진행: {game_data['players'][game_data['current_player_idx']]}")

    def finish_game(all_dead=False):
        """5번 조건: 최종 결과 발표"""
        remaining = game_data["players"][game_data["current_player_idx"]:]
        game_data["survivors"].extend(remaining)
        
        game_view.visible = False
        result_view.visible = True
        
        res_survivors.value = f"⭕ 생존자: {', '.join(game_data['survivors']) if game_data['survivors'] else '없음'}"
        res_dead.value = f"❌ 사망자: {', '.join(game_data['dead']) if game_data['dead'] else '없음'}"
        page.update()

    def reset_all(e):
        setup_view.visible = True
        result_view.visible = False
        page.update()

    # --- 화면 레이아웃 구성 ---
    # 1단계: 설정 화면
    setup_view = ft.Column([
        ft.Text("Step 1: 게임 설정", size=25, weight="bold"),
        ft.Row([player_count_ref, bridge_len_ref]),
        ft.ElevatedButton("다음 (이름 입력)", icon="arrow_forward", on_click=create_name_fields)
    ])

    # 2단계: 이름 입력 화면
    name_view = ft.Column([
        ft.Text("Step 2: 참가자 이름 입력", size=25, weight="bold"),
        name_inputs_col,
        ft.ElevatedButton("게임 시작!", icon="play_arrow", on_click=start_game)
    ], visible=False)

    # 3단계: 게임 진행 화면
    step_info = ft.Text("", size=25, weight="bold")
    player_info = ft.Text("", size=20, color="cyan")
    game_view = ft.Column([
        step_info,
        player_info,
        ft.Row([
            ft.ElevatedButton("왼쪽(L)", on_click=handle_choice, data="L", bgcolor="blue", color="white", expand=True),
            ft.ElevatedButton("오른쪽(R)", on_click=handle_choice, data="R", bgcolor="red", color="white", expand=True),
        ]),
        ft.Text("진행 로그:"),
        log_list
    ], visible=False)

    # 4단계: 결과 발표 화면
    res_survivors = ft.Text("", size=20, color="green")
    res_dead = ft.Text("", size=20, color="red")
    result_view = ft.Column([
        ft.Text("🏆 최종 결과", size=30, weight="bold"),
        res_survivors,
        res_dead,
        ft.ElevatedButton("다시 시작", icon="refresh", on_click=reset_all)
    ], visible=False)

    page.add(status_text, ft.Divider(), setup_view, name_view, game_view, result_view)

ft.app(target=main)
