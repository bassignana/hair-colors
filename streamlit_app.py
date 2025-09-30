import streamlit as st
import random
import os
import pandas as pd
from supabase import create_client


def main():
    # st.write(st.session_state)
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com/bassignana/hair-colors/main/colors"
    supabase = create_client(st.secrets['URL'], st.secrets['KEY'])

    script_dir = os.path.dirname(__file__)
    colors_folder_path = os.path.join(script_dir, 'colors')

    def callback():
        current_file = st.session_state.file_names[st.session_state.counter]
        st.session_state.result[current_file] = st.session_state[
            f'choice_{st.session_state.counter}']
        st.session_state.counter += 1

    test, classifica, risultati = st.tabs(['Test', 'Classifica', 'Risultati'])

    with test:
        if 'file_names' not in st.session_state:
            names = os.listdir(colors_folder_path)
            random.shuffle(names)
            st.session_state.file_names = [name.split('.')[0] for name in names]

        if 'result' not in st.session_state:
            st.session_state.result = {}

        if 'counter' not in st.session_state:
            st.session_state.counter = 0

        if 'nickname' not in st.session_state:
            st.session_state.nickname = ''

        if 'can_proceed' not in st.session_state:
            st.session_state.can_proceed = False

        if not st.session_state.can_proceed:
            with st.form("save_test_form"):
                test_id = st.text_input("Crea un nome per il tuo test, se vuoi eh. No scherzo, devi.",
                                        st.session_state.nickname)
                submitted = st.form_submit_button("Salva")

            if submitted:
                existing = supabase.table("test_results").select("*").eq("test_id", test_id).execute()

                if not existing.data:
                    st.session_state.nickname = test_id
                    st.session_state.can_proceed = True
                    st.rerun()
                else:
                    st.error(
                        "Nome già esistente, mannaggia al papelo, scegline un altro e non mi rompere il database.")
        else:
            if st.session_state.counter < len(st.session_state.file_names):
                with st.form(key=str(st.session_state.counter)):
                    st.image(f'{colors_folder_path}/{st.session_state.file_names[st.session_state.counter]}.jpg')
                    st.radio("Scegli il colore", ["biondo", "castano", "nero"],
                             key=f'choice_{st.session_state.counter}')

                    st.form_submit_button('Conferma', on_click=callback)
            else:
                st.success("Congratulazioni, per così dire. Controlla ora il tab risultati e classifica.")
                # calculate the result in other dict
                # save the original dict, the result, the nickname for
                # use a dataframe, calculate columns
                df = pd.DataFrame(list(st.session_state.result.items()),
                                  columns=['Vero Nome', 'La Tua Scelta'])

                df.insert(0, 'Immagine', df['Vero Nome'].apply(
                    lambda x: f'{GITHUB_RAW_BASE}/{x}.jpg'
                ))

                df = df.sort_values('Vero Nome')
                df['Corretto'] = (df['Vero Nome'].str.split('_').str[0] == df['La Tua Scelta']).astype(int)

                st.dataframe(
                    df,
                    column_config={
                        "Immagine": st.column_config.ImageColumn(
                            "Immagine",
                            width="small"
                        )
                    },
                    hide_index=True
                )

                df_save = df.copy()
                df_save.columns = [column.lower().replace(' ','_') for column in df_save.columns]
                df_save = df_save.drop('immagine', axis = 1)

                records = df_save.to_dict('records')
                for record in records:
                    record['test_id'] = st.session_state.nickname

                supabase.table("test_results").insert(records).execute()

                if st.button("Prova ancora"):
                    del st.session_state.result
                    del st.session_state.counter
                    del st.session_state.nickname
                    del st.session_state.can_proceed
                    st.rerun()

    with classifica:
            data = supabase.table("test_results").select("*").execute()
            if data.data:
                df_all = pd.DataFrame(data.data)

                ranking = df_all.groupby('test_id')['corretto'].agg(['sum']).reset_index()
                ranking.columns = ['test_id', 'corretti']
                ranking = ranking.sort_values('corretti', ascending=False)

                st.dataframe(ranking, hide_index=True)
    with risultati:
        data = supabase.table("test_results").select("*").execute()
        if data.data:
            df_all = pd.DataFrame(data.data)

            for test_id in df_all['test_id'].unique():
                st.write(f"Nome del test: {test_id}")
                test_df = df_all[df_all['test_id'] == test_id][['vero_nome', 'la_tua_scelta', 'corretto']].copy()
                test_df.insert(0, 'immagine', test_df['vero_nome'].apply(lambda x: f'{GITHUB_RAW_BASE}/{x}.jpg'))
                st.dataframe(
                    test_df,
                    column_config={
                        "immagine": st.column_config.ImageColumn("Immagine", width="medium")
                    },
                    hide_index=True
                )

if __name__ == "__main__":
    main()
