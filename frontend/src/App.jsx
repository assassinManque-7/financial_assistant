import { useState } from "react"

function App(){
  const [doc, setDoc] = useState("");
  const [res, setRes] = useState("");

  const send_gem = async (inp) => {
    const resp = await fetch(
      "http://127.0.0.1:8000/analyze",
      
      {
        method : "POST",

        headers : {
          "Content-Type" : "application/json"
        },

        body : JSON.stringify(
          {"docs" : inp}
        ),
      }

    );

    const data = await resp.json();

    setRes(data.response);
  }

  return (
    <>
      <input 
        value = {doc}
        placeholder = "doc"
        onChange = {(e) => {setDoc(e.target.value)}}
      />

      <button onClick = {() => send_gem(doc)}>
        analyze
      </button>

      <textarea
        value = {res}
      />
    </>
  )

}

export default App;