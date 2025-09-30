import streamlit as st
import random
import os
import pandas as pd
from PIL import Image


def main():
    st.write(st.session_state)
    script_dir = os.path.dirname(__file__)
    colors_folder_path = os.path.join(script_dir, 'colors')

    def callback():
        current_file = st.session_state.file_names[st.session_state.counter]
        st.session_state.result[current_file] = st.session_state[
            f'choice_{st.session_state.counter}']
        st.session_state.counter += 1

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

        df.insert(0, 'Immagine', df['Vero Nome'].apply(lambda x: f'{colors_folder_path}/{x}.jpg'))

        # Display with images
        st.dataframe(
            df,
            column_config={
                "Immagine": st.column_config.ImageColumn(
                    "Immagine",
                    pinned = True
                )
            },
            hide_index=True
        )

        st.write(df.to_dict())

        if st.button("Prova ancora"):
            st.rerun()


if __name__ == "__main__":
    main()
