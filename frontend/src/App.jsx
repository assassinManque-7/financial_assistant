import { useState } from "react"

function App(){
  const [doc, setDoc] = useState(null);
  const [res, setRes] = useState(null);
  const [error, setError] = useState(null);

  const choose_pdf = (e) => {
    const chosen_pdf = e.target.files[0];

    if (!chosen_pdf) return;

    setDoc(chosen_pdf)

  }


  const upload_pdf = async () => {
    if (!doc){
      setError("select a pdf first");
      return;
    }

    const formdata = new FormData()

    formdata.append('file', doc)

    const resp = await fetch(
      "http://127.0.0.1:8000/read_pdf",
      
      {
        method : "POST",

        body : formdata,
      }

    );

    const data = await resp.json();

    setRes(data.text);
  }

  return (
    <>
      <input 
        type = "file"
        accept = ".pdf"
        onChange = {choose_pdf}
      />

      <button onClick = {() => upload_pdf(doc)}>
        extract text
      </button>

      <textarea
        value = {res}
      />
    </>
  )

}

export default App;