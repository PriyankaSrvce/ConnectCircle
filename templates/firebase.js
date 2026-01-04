<script type="module">
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyDyZV7_NJURsYtOK311V4b13NG3uHv3tog",
  authDomain: "elderlyease-7be75.firebaseapp.com",
  projectId: "elderlyease-7be75",
  storageBucket: "elderlyease-7be75.appspot.com",
  messagingSenderId: "933473196",
  appId: "1:933473196:web:902488f3ce1317c333a809"
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
</script>