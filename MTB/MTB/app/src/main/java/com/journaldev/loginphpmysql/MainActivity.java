package com.journaldev.loginphpmysql;


import android.content.Intent;
import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Patterns;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

public class MainActivity extends AppCompatActivity {
    int success;
    JSONObject json;

    EditText editEmail, editPassword, editName;
    Button btnSignIn, btnRegister,btnBack;


    boolean isEmailValid, isPasswordValid, isNameValid;

    String URL= "http://192.168.64.2/xampp_php/index.php";

    String act;

    JSONParser jsonParser=new JSONParser();

    int i=0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        editEmail=(EditText)findViewById(R.id.editEmail);
        editName=(EditText)findViewById(R.id.editName);
        editPassword=(EditText)findViewById(R.id.editPassword);

        btnSignIn=(Button)findViewById(R.id.btnSignIn);
        btnRegister=(Button)findViewById(R.id.btnRegister);
        btnBack=(Button)findViewById(R.id.btnBack);

        btnSignIn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                act="log in";
                // Check for a valid name.
                if (editName.getText().toString().isEmpty()) {
                    editName.setError(getResources().getString(R.string.name_error));
                    isNameValid = false;
                } else  {
                    isNameValid = true;
                }


                // Check for a valid password.
                if (editPassword.getText().toString().isEmpty()) {
                    editPassword.setError(getResources().getString(R.string.password_error));
                    isPasswordValid = false;
                } else if (editPassword.getText().length() < 6) {
                    editPassword.setError(getResources().getString(R.string.error_invalid_password));
                    isPasswordValid = false;
                } else  {
                    isPasswordValid = true;
                }

                if (isNameValid && isPasswordValid) {
                    AttemptLogin attemptLogin = new AttemptLogin();
                    attemptLogin.execute(editName.getText().toString(), editPassword.getText().toString(), "");
                }
            }
        });

        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                btnRegister.setText("CREATE AN ACCOUNT");
                btnBack.setVisibility(View.GONE);
                editEmail.setVisibility(View.GONE);
                btnSignIn.setVisibility(View.VISIBLE);
                i=0;
            }
        });

        btnRegister.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View view) {
                act="register";


                if(i==0)
                {
                    i=1;
                    editEmail.setVisibility(View.VISIBLE);
                    btnBack.setVisibility(View.VISIBLE);
                    btnSignIn.setVisibility(View.GONE);
                    btnRegister.setText("REGISTER");
                }
                else{

                    // Check for a valid name.
                    if (editName.getText().toString().isEmpty()) {
                        editName.setError(getResources().getString(R.string.name_error));
                        isNameValid = false;
                    } else  {
                        isNameValid = true;
                    }

                    // Check for a valid email address.
                    if (editEmail.getText().toString().isEmpty()) {
                        editEmail.setError(getResources().getString(R.string.email_error));
                        isEmailValid = false;
                    } else if (!Patterns.EMAIL_ADDRESS.matcher(editEmail.getText().toString()).matches()) {
                        editEmail.setError(getResources().getString(R.string.error_invalid_email));
                        isEmailValid = false;
                    } else  {
                        isEmailValid = true;
                    }


                    // Check for a valid password.
                    if (editPassword.getText().toString().isEmpty()) {
                        editPassword.setError(getResources().getString(R.string.password_error));
                        isPasswordValid = false;
                    } else if (editPassword.getText().length() < 6) {
                        editPassword.setError(getResources().getString(R.string.error_invalid_password));
                        isPasswordValid = false;
                    } else  {
                        isPasswordValid = true;
                    }

                    if (isNameValid && isEmailValid && isPasswordValid) {

                        AttemptLogin attemptLogin = new AttemptLogin();
                        attemptLogin.execute(editName.getText().toString(), editPassword.getText().toString(), editEmail.getText().toString());

                    }
                }
            }
        });


    }

    public class AttemptLogin extends AsyncTask<String, String, JSONObject> {
        @Override

        protected void onPreExecute() {



            super.onPreExecute();

        }

        @Override

        public JSONObject doInBackground(String... args) {



            String email = args[2];
            String password = args[1];
            String name= args[0];

            ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
            params.add(new BasicNameValuePair("username", name));
            params.add(new BasicNameValuePair("password", password));
            if(email.length()>0)
                params.add(new BasicNameValuePair("email",email));

            json = jsonParser.makeHttpRequest(URL, "POST", params);
            return json;
        }

        protected void onPostExecute(JSONObject result) {
            // dismiss the dialog once product deleted
            // Toast.makeText(getApplicationContext(),result,Toast.LENGTH_LONG).show();
            try {
                if (result != null) {
                    Toast.makeText(getApplicationContext(),result.getString("message"),Toast.LENGTH_LONG).show();
                    success=result.getInt("success");
                    if (success==1){
                        if (act=="register") {
                            btnRegister.setText("CREATE AN ACCOUNT");
                            btnBack.setVisibility(View.GONE);
                            editEmail.setVisibility(View.GONE);
                            btnSignIn.setVisibility(View.VISIBLE);
                            i = 0;
                        }
                        if (act=="log in") {
                            Intent intent = new Intent(getApplicationContext(), Tabs.class);
                            startActivity(intent);
                        }
                    }

                } else {
                    Toast.makeText(getApplicationContext(), "Unable to retrieve any data from server", Toast.LENGTH_LONG).show();
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

}
