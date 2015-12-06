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
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    // ListView which contains all plugItems.
    private ListView listView;
    // List of plugItems that are contained in the listView.
    private Plug[] plugItems;
    // Server address.
    private String serveraddress;
    // Server port.
    private int port;
    // SharedPreference (used to store e.g. serveraddress and port).
    private SharedPreferences sharedPreferences;
    // Temporal plug. Used to add a plug to the server list.
    private Plug plug;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // Set initial SharedPreferences.
        this.sharedPreferences = this.getPreferences(Context.MODE_PRIVATE);
        this.serveraddress = sharedPreferences.getString(getString(R.string.saved_serveraddress), "cslectures.tongsucn.com");
        this.port = sharedPreferences.getInt(getString(R.string.saved_serverport), 8123);

        // Initiate listView.
        this.listView = (ListView) findViewById(R.id.listViewPlug);
        this.listView.setOnItemClickListener(new OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                onListViewClick(position);
            }
        });

        // Initiate other objects.
        this.plug = new Plug();
        this.plugItems = new Plug[0];

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
        this.plug = this.plugItems[position];
        new SwitchAsyncTask().execute();
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

            case R.id.action_add:
                this.addPlug();
                break;

            case R.id.action_delete:
                this.deletePlug();
                break;

            default:
                break;
        }

        return super.onOptionsItemSelected(item);
    }

    /**
     * Edit the server address.
     */
    private void editServerAddress() {
        final EditText editTextServerAddress = new EditText(this);
        editTextServerAddress.setText(this.serveraddress);
        editTextServerAddress.setSingleLine(true);

        new AlertDialog.Builder(this)
                .setTitle("Server address")
                .setMessage("Please enter the server address!")
                .setView(editTextServerAddress)
                .setPositiveButton("Confirm", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        serveraddress = editTextServerAddress.getText().toString();

                        // Save new address in preferences.
                        SharedPreferences.Editor editor = sharedPreferences.edit();
                        editor.putString(getString(R.string.saved_serveraddress), serveraddress);
                        editor.apply();
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
    private void editServerPort() {
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
    private void refresh() {
        new ReceiveAsyncTask().execute();
    }

    /**
     * Add a plug and send it to the server.
     */
    private void addPlug() {
        final EditText editTextPlugDescription = new EditText(this);
        editTextPlugDescription.setText(this.plug.getDescription());
        editTextPlugDescription.setSingleLine(true);

        new AlertDialog.Builder(this)
                .setTitle("New plug")
                .setMessage("Please enter a description for the plug (max. 16 letters)!")
                .setView(editTextPlugDescription)
                .setPositiveButton("Confirm", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        String description = editTextPlugDescription.getText().toString();

                        // Check that description has a correct length.
                        if (description.length() > 16) {
                            Toast.makeText(getApplicationContext(),
                                    "The description must not be longer than 16 letters!",
                                    Toast.LENGTH_LONG).show();
                            return;
                        } else if (description.isEmpty()) {
                            Toast.makeText(getApplicationContext(),
                                    "The description must not be empty!",
                                    Toast.LENGTH_LONG).show();
                            return;
                        }

                        // Check if description does not exist yet.
                        if (getPlugDescriptions().contains(description)) {
                            Toast.makeText(getApplicationContext(),
                                    "The description already exists!",
                                    Toast.LENGTH_LONG).show();
                            return;
                        }

                        plug.setDescription(description);
                        addPlugSub();
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                    }
                })
                .show();
    }

    /**
     * Submethod of addPlug(). Don't use it!
     */
    private void addPlugSub() {
        final EditText editTextPlugID = new EditText(this);
        editTextPlugID.setText(this.plug.getId());
        editTextPlugID.setSingleLine(true);
        editTextPlugID.setInputType(InputType.TYPE_CLASS_NUMBER);

        new AlertDialog.Builder(this)
                .setTitle("New plug")
                .setMessage("Please enter the id of the plug (10 binary digits)!")
                .setView(editTextPlugID)
                .setPositiveButton("Confirm", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        String id = editTextPlugID.getText().toString();
                        // Check length.
                        if (id.length() != 10) {
                            Toast.makeText(getApplicationContext(),
                                    "The id of the plug must contain 10 binary digits!",
                                    Toast.LENGTH_LONG).show();
                            return;
                        }
                        // Check if binary.
                        if (!id.matches("[01]+")) {
                            Toast.makeText(getApplicationContext(),
                                    "The id of the plug must only contain binary digits!",
                                    Toast.LENGTH_LONG).show();
                            return;
                        }

                        plug.setId(id);

                        // Send new plug to server.
                        new PlugAddAsyncTask().execute();
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                    }
                })
                .show();
    }

    /**
     * Delete a plug and send it to a server.
     */
    private void deletePlug() {
        final Spinner spinnerDeletePlug = new Spinner(this);
        List<String> descriptions = this.getPlugDescriptions();

        ArrayAdapter<String> dataAdapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_dropdown_item, descriptions);
        dataAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerDeletePlug.setAdapter(dataAdapter);

        new AlertDialog.Builder(this)
                .setTitle("Delete plug")
                .setMessage("Please choose the plug which will be deleted!")
                .setView(spinnerDeletePlug)
                .setPositiveButton("Confirm", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        plug = plugItems[(int) spinnerDeletePlug.getSelectedItemId()];

                        // Send the removed plug to server.
                        new PlugDeleteAsyncTask().execute();
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                    }
                })
                .show();
    }

    private List<String> getPlugDescriptions() {
        List<String> descriptions = new ArrayList<>();

        for (Plug p : this.plugItems)
            descriptions.add(p.getDescription());

        return descriptions;
    }

    /**
     * Send data to the server to inform server of switch.
     */
    private class SwitchAsyncTask extends AsyncTask<Void, Void, String> {
        protected String doInBackground(Void... params) {
            try {
                InetAddress inetAddress = InetAddress.getByName(serveraddress);

                Socket socket = new Socket();
                socket.connect(new InetSocketAddress(inetAddress, port), 10000);

                // Send.
                DataOutputStream dataOutputStream = new DataOutputStream(socket.getOutputStream());
                String binaryStr = "01" + plug.getId() + (plug.getState() ? "10" : "01") + "00";
                Short s = Short.parseShort(binaryStr, 2);
                dataOutputStream.writeShort(s);

                socket.close();
            } catch (Exception e) {
                return e.toString();
            }

            // Success.
            return null;
        }

        protected void onPostExecute(String result) {
            if (result != null)
                Toast.makeText(MainActivity.this.getApplicationContext(),
                        "Could not switch the plug: \n" + result,
                        Toast.LENGTH_LONG).show();
            else
                MainActivity.this.refresh();
        }
    }

    /**
     * Receive data from server and updates the listView.
     */
    private class ReceiveAsyncTask extends AsyncTask<Void, Void, String> {
        protected String doInBackground(Void... params) {
            try {
                InetAddress inetAddress = InetAddress.getByName(serveraddress);

                Socket socket = new Socket();
                socket.connect(new InetSocketAddress(inetAddress, port), 10000);

                // Send.
                DataOutputStream dataOutputStream = new DataOutputStream(socket.getOutputStream());
                dataOutputStream.writeShort(0x00);

                // Receive.
                BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                // Fill listView with items.
                String result = "", line;
                while ((line = bufferedReader.readLine()) != null)
                    result += line;
                List<Plug> plugList = new ArrayList<>();
                String[] separated = result.split(";");
                try { // The following lines are a bit volatile, if something happens, just let it crash.
                    for (int i = 0; i < separated.length - 2; i += 3) {
                        Boolean status = "on".equals(separated[i + 2]);
                        plugList.add(new Plug(separated[i], separated[i + 1], status));
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }

                MainActivity.this.plugItems = plugList.toArray(new Plug[plugList.size()]);

                socket.close();
                return null;
            } catch (Exception e) {
                return e.toString();
            }
        }

        protected void onPostExecute(String result) {
            if (result != null && !result.equals(""))
                Toast.makeText(MainActivity.this.getApplicationContext(),
                        "Could not fetch the server data: \n" + result,
                        Toast.LENGTH_LONG).show();
            else {
                // Show plugs in listview.
                CustomAdapter customAdapter = new CustomAdapter(MainActivity.this, MainActivity.this.plugItems);
                MainActivity.this.listView.setAdapter(customAdapter);
            }
        }
    }

    /**
     * Send data to server to add a plug.
     */
    private class PlugAddAsyncTask extends AsyncTask<Void, Void, String> {
        protected String doInBackground(Void... params) {
            try {
                InetAddress inetAddress = InetAddress.getByName(serveraddress);

                Socket socket = new Socket();
                socket.connect(new InetSocketAddress(inetAddress, port), 10000);

                // Send.
                DataOutputStream dataOutputStream = new DataOutputStream(socket.getOutputStream());

                String name = plug.getDescription();
                byte [] encodeName = name.getBytes();

                String binaryStr = "11" + plug.getId();
                Integer i = Integer.parseInt(binaryStr, 2) << 4;
                i |= name.length();
                byte [] frontField = ByteBuffer.allocate(4).putInt(i).array();

                byte [] data = new byte[2 + name.length()];
                System.arraycopy(frontField, 2, data, 0, 1);
                System.arraycopy(frontField, 3, data, 1, 1);
                System.arraycopy(encodeName, 0, data, 2, name.length());

                dataOutputStream.write(data);

                socket.close();
            } catch (Exception e) {
                return e.toString();
            }

            // Success.
            return null;
        }

        protected void onPostExecute(String result) {
            if (result != null)
                Toast.makeText(MainActivity.this.getApplicationContext(),
                        "Could not add plug: \n" + result,
                        Toast.LENGTH_LONG).show();
            else
                MainActivity.this.refresh();
        }
    }

    /**
     * Send data to server to remove a plug.
     */
    private class PlugDeleteAsyncTask extends AsyncTask<Void, Void, String> {
        protected String doInBackground(Void... params) {
            try {
                InetAddress inetAddress = InetAddress.getByName(serveraddress);

                Socket socket = new Socket();
                socket.connect(new InetSocketAddress(inetAddress, port), 10000);

                // Send.
                DataOutputStream dataOutputStream = new DataOutputStream(socket.getOutputStream());
                // TODO: update format.
                String binaryStr = "10" + plug.getId();
                Short s = Short.parseShort(binaryStr, 2);
                dataOutputStream.writeShort(s * 16);

                socket.close();
            } catch (Exception e) {
                return e.toString();
            }

            // Success.
            return null;
        }

        protected void onPostExecute(String result) {
            if (result != null)
                Toast.makeText(MainActivity.this.getApplicationContext(),
                        "Could not remove plug: \n" + result,
                        Toast.LENGTH_LONG).show();
            else
                MainActivity.this.refresh();
        }
    }
}