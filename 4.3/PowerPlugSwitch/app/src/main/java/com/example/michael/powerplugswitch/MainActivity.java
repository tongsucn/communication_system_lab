package com.example.michael.powerplugswitch;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.InputType;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.Socket;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

// TODO: TLS connection.

public class MainActivity extends AppCompatActivity {
    // ListView which contains all plugItems.
    private ListView listView;
    // List of plugItems that are contained in the listView.
    private Plug[] plugItems;
    // Serveraddress.
    private String serveraddress;
    // Server port.
    private int port;
    // SharedPreference (used to store e.g. serveraddress and port).
    SharedPreferences sharedPreferences;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // Set initial SharedPreferences.
        this.sharedPreferences = this.getPreferences(Context.MODE_PRIVATE);
        this.serveraddress = sharedPreferences.getString(getString(R.string.saved_serveraddress), "tongsucn.com");
        this.port = sharedPreferences.getInt(getString(R.string.saved_serverport), 1234);

        // Initiate listView.
        this.listView = (ListView) findViewById(R.id.listViewPlug);

        this.listView.setOnItemClickListener(new OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                onListViewClick(position);
            }
        });

        // Get data from server.
        this.refresh();
    }

    /**
     * Called when listView item got clicked.
     * Updates the listView and especially its checkboxes.
     *
     * @param position Position of item in listView.
     */
    private void onListViewClick(int position) {
        this.plugItems[position].changeState();

        CustomAdapter customAdapter = new CustomAdapter(this, this.plugItems);
        this.listView.setAdapter(customAdapter);

        // Send update to server.
        new SendAsyncTask().execute(
                this.serveraddress,
                String.valueOf(this.port),
                this.plugItems[position].getId(),
                this.plugItems[position].getState().toString());
    }

    /**
     * Auto-generated method.
     *
     * @param menu menu item
     * @return true
     */
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    /**
     * Decide what to do when options are used.
     *
     * @param item The item that got clicked
     * @return true
     */
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {

            case R.id.action_serveraddress:
                this.editServerAddress();
                break;

            case R.id.action_serverport:
                this.editServerPort();
                break;

            case R.id.action_refresh:
                this.refresh();
                break;

            default:
                break;
        }

        return super.onOptionsItemSelected(item);
    }

    /**
     * Edit the server address.
     */
    public void editServerAddress() {
        final EditText editTextServerAddress = new EditText(this);
        editTextServerAddress.setText(this.serveraddress);
        editTextServerAddress.setSingleLine(true);

        new AlertDialog.Builder(this)
                .setTitle("Server address")
                .setMessage("Please enter the server address!")
                .setView(editTextServerAddress)
                .setPositiveButton("Confirm", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        try {
                            // Check if input is a valid URL.
                            String url = editTextServerAddress.getText().toString();
                            if (!url.startsWith("http://"))
                                url = "http://" + url;
                            new URL(url);

                            serveraddress = url;

                            // Save new address in preferences.
                            SharedPreferences.Editor editor = sharedPreferences.edit();
                            editor.putString(getString(R.string.saved_serveraddress), serveraddress);
                            editor.apply();
                        } catch (MalformedURLException mue) {
                            Toast.makeText(getApplicationContext(),
                                    "Input was not a correct URL",
                                    Toast.LENGTH_LONG)
                                    .show();
                        }
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                    }
                })
                .show();
    }

    /**
     * Edit the server port.
     */
    public void editServerPort() {
        final EditText editTextServerPort = new EditText(this);
        editTextServerPort.setText(String.valueOf(this.port));
        editTextServerPort.setInputType(InputType.TYPE_CLASS_NUMBER);
        editTextServerPort.setSingleLine(true);

        new AlertDialog.Builder(this)
                .setTitle("Server port")
                .setMessage("Please enter the server port!")
                .setView(editTextServerPort)
                .setPositiveButton("Confirm", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        try {
                            // Check if number has the correct format.
                            if (Integer.parseInt(editTextServerPort.getText().toString()) < 1024
                                    || Integer.parseInt(editTextServerPort.getText().toString()) > 65535) {
                                Toast.makeText(getApplicationContext(),
                                        "This is not a correct port. Use a port between 1024 and 65535",
                                        Toast.LENGTH_LONG)
                                        .show();
                            } else {
                                port = Integer.parseInt(editTextServerPort.getText().toString());
                                // Save new port in preferences.
                                SharedPreferences.Editor editor = sharedPreferences.edit();
                                editor.putInt(getString(R.string.saved_serverport), port);
                                editor.apply();
                            }
                        } catch (NumberFormatException nfe) {
                            Toast.makeText(getApplicationContext(),
                                    "Input was not a correct number",
                                    Toast.LENGTH_LONG)
                                    .show();
                        }
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                    }
                })
                .show();
    }

    /**
     * Refresh the listView with fresh server data.
     */
    public void refresh() {
        new ReceiveAsyncTask().execute(
                this.serveraddress,
                String.valueOf(this.port));
    }

    /**
     * Send data to the server to inform server of update.
     */
    private class SendAsyncTask extends AsyncTask<String, Void, String> {
        protected String doInBackground(String... params) {

            String serveraddress = params[0];
            int port = Integer.parseInt(params[1]);
            String id = params[2];                          // Plug id.
            Boolean state = Boolean.valueOf(params[3]);     // true = plug on, false = plug off.

            // TODO: work here!
            /*
            try {
                Socket socket = new Socket(serveraddress, port);
                DataOutputStream dataOutputStream = new DataOutputStream(socket.getOutputStream());
                dataOutputStream.writeUTF(message);
                socket.close();
            } catch (Exception e) {
                return e.toString();
            }
            */
            return "Successfully changed the plug";
        }

        protected void onPostExecute(String result) {
            Toast.makeText(MainActivity.this.getApplicationContext(), result, Toast.LENGTH_LONG).show();
        }
    }

    /**
     * Receive data from server and updates the listView.
     */
    private class ReceiveAsyncTask extends AsyncTask<String, Void, String> {
        protected String doInBackground(String... params) {

            String serveraddress = params[0];
            int port = Integer.parseInt(params[1]);
            String result = "";

            // TODO: work here!
            /*
            try {
                Socket socket = new Socket(serveraddress, port);
                BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                String line;
                while ((line = bufferedReader.readLine()) != null)
                    result += line;

                socket.close();
            } catch (Exception e) {
                return e.toString();
            }*/

            return result;
        }

        protected void onPostExecute(String result) {
            Toast.makeText(MainActivity.this.getApplicationContext(), result, Toast.LENGTH_LONG).show();

            // TODO: remove dummy result string.
            result = "00001;Lamp Livingroom;true;00010;Lamp Kitchen;false;00011;Coffeemachine;true;00100;Computer;true;"
                + "00101;Herd;false;00110;Roller Shutter Kitchen;false;00111;Roller Shutter Livingroom;true;"
                + "01000;Roller Shutter Bedroom;false";

            List<Plug> plugList = new ArrayList<>();
            String[] separated = result.split(";");

            for (int i = 0; i < separated.length; i+= 3) {
                plugList.add(new Plug(separated[i], separated[i+1], Boolean.valueOf(separated[i + 2])));
            }

            MainActivity.this.plugItems = plugList.toArray(new Plug[plugList.size()]);
            CustomAdapter customAdapter = new CustomAdapter(MainActivity.this, MainActivity.this.plugItems);
            MainActivity.this.listView.setAdapter(customAdapter);
        }
    }

}