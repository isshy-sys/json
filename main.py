import streamlit as st
import json
import requests
from io import StringIO

def main():
    st.title("📄 JSON可視化アプリ")
    st.markdown("JSONファイルやAPI から取得したデータをインタラクティブに表示します")
    
    # サイドバーで入力方法を選択
    st.sidebar.title("データ入力方法")
    input_method = st.sidebar.selectbox(
        "データの取得方法を選択してください",
        ["JSONファイルをアップロード", "API連携で取得"],
        index=1  # 「API連携で取得」を初期選択にする
    )
    
    json_data = None
    
    if input_method == "JSONファイルをアップロード":
        json_data = handle_file_upload()
    else:
        json_data = handle_api_request()
    
    # JSONデータが取得できた場合に表示
    if json_data is not None:
        display_json_data(json_data)

def handle_file_upload():
    """ファイルアップロード処理"""
    st.header("📁 JSONファイルをアップロード")
    uploaded_file = st.file_uploader(
        "JSONファイルを選択してください",
        type=['json'],
        help="JSONファイル(.json)をアップロードしてください"
    )
    
    if uploaded_file is not None:
        try:
            # ファイルを読み込んでJSONとしてパース
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            json_data = json.load(stringio)
            
            st.success(f"✅ ファイル '{uploaded_file.name}' を正常に読み込みました")
            return json_data
            
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON形式が正しくありません: {str(e)}")
        except Exception as e:
            st.error(f"❌ ファイルの読み込みに失敗しました: {str(e)}")
    
    return None

def handle_api_request():
    """API連携処理"""
    st.header("🌐 API連携でJSONデータを取得")
    
    # API URLの入力
    api_url = st.text_input(
        "API URL",
        placeholder="https://api.example.com/data",
        help="JSON形式のデータを返すAPIのURLを入力してください"
    )
    
    # APIキーやヘッダーの設定（オプション）
    with st.expander("🔧 詳細設定（オプション）"):
        headers = {}
        
        # APIキー
        api_key = st.text_input(
            "APIキー",
            type="password",
            help="必要に応じてAPIキーを入力してください"
        )
        if api_key:
            auth_header = st.selectbox(
                "認証ヘッダー形式",
                ["Authorization: Bearer", "Authorization: API-Key", "X-API-Key"]
            )
            if auth_header == "Authorization: Bearer":
                headers["Authorization"] = f"Bearer {api_key}"
            elif auth_header == "Authorization: API-Key":
                headers["Authorization"] = f"API-Key {api_key}"
            else:
                headers["X-API-Key"] = api_key
        
        # カスタムヘッダー
        custom_headers = st.text_area(
            "カスタムヘッダー (JSON形式)",
            placeholder='{"Content-Type": "application/json"}',
            help="追加のヘッダーをJSON形式で入力してください"
        )
        if custom_headers:
            try:
                custom_headers_dict = json.loads(custom_headers)
                headers.update(custom_headers_dict)
            except json.JSONDecodeError:
                st.warning("カスタムヘッダーのJSON形式が正しくありません")
    
    # APIリクエスト実行ボタン
    if st.button("🚀 データを取得", disabled=not api_url):
        if api_url:
            try:
                with st.spinner("データを取得中..."):
                    response = requests.get(api_url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    json_data = response.json()
                    st.success(f"✅ APIからデータを正常に取得しました (ステータス: {response.status_code})")
                    return json_data
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ APIリクエストに失敗しました: {str(e)}")
            except json.JSONDecodeError:
                st.error("❌ レスポンスがJSON形式ではありません")
            except Exception as e:
                st.error(f"❌ 予期しないエラーが発生しました: {str(e)}")
    
    return None

def display_json_data(json_data):
    """JSONデータの表示処理"""
    st.header("📊 JSONデータの可視化")
    
    # 基本情報の表示
    col1, col2 = st.columns(2)
    with col1:
        data_type = type(json_data).__name__
        st.metric("データ型", data_type)
    with col2:
        if isinstance(json_data, (list, dict)):
            size = len(json_data)
            st.metric("要素数", size)
    
    # タブで表示方法を分ける
    tab1, tab2, tab3 = st.tabs(["🎯 インタラクティブ表示", "📝 生JSON", "📋 データ構造"])
    
    with tab1:
        st.subheader("インタラクティブなJSON表示")
        st.json(json_data, expanded=False)
    
    with tab2:
        st.subheader("生JSONデータ")
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        st.code(json_str, language='json')
        
        # ダウンロードボタン
        st.download_button(
            label="📥 JSONファイルをダウンロード",
            data=json_str,
            file_name="data.json",
            mime="application/json"
        )
    
    with tab3:
        st.subheader("データ構造の分析")
        analyze_json_structure(json_data)

def analyze_json_structure(data, prefix=""):
    """JSON構造の分析表示"""
    if isinstance(data, dict):
        st.write(f"**{prefix if prefix else 'Root'}** (辞書型 - {len(data)} keys)")
        for key, value in data.items():
            value_type = type(value).__name__
            if isinstance(value, (dict, list)):
                st.write(f"  • `{key}`: {value_type}")
                if len(str(value)) < 1000:  # 大きすぎるデータの再帰を避ける
                    analyze_json_structure(value, f"{prefix}.{key}" if prefix else key)
            else:
                preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                st.write(f"  • `{key}`: {value_type} = {preview}")
    
    elif isinstance(data, list):
        st.write(f"**{prefix if prefix else 'Root'}** (配列型 - {len(data)} items)")
        if data:
            first_item_type = type(data[0]).__name__
            st.write(f"  • 要素型: {first_item_type}")
            if len(data) <= 3:  # 最初の数個だけ表示
                for i, item in enumerate(data):
                    if isinstance(item, (dict, list)) and len(str(item)) < 500:
                        analyze_json_structure(item, f"{prefix}[{i}]" if prefix else f"[{i}]")

if __name__ == "__main__":
    # ページ設定
    st.set_page_config(
        page_title="JSON可視化アプリ",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # メイン処理
    main()