package com.example.michael.shake;

import android.app.ProgressDialog;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.view.ViewPager;
import android.view.View;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Toast;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;

/**
 * GUI class. Handles all events.
 */
public class MainActivity extends FragmentActivity implements SensorEventListener {
    // Manage sensors.
    private SensorManager mSensorManager;
    private Sensor mAccelerometer;          // Accelerometer.
    private Sensor mGyroscope;              // Gyroscope.
    private Sensor mMagnetometer;           // Magnetometer.
    private Sensor mBarometer;              // Barometer.

    // Stores initial values for accelerometer.
    private float[] calibrationReference;

    private enum ShakeDirection {zero, xPos, xNeg, yPos, yNeg, zPos, zNeg}

    private ShakeDirection shakeDirection = ShakeDirection.zero;

    // Current page.
    private enum Page {
        Accelerometer, Gyroscope, Magnetometer, Barometer
    }

    private Page currentPage = Page.Accelerometer;

    // Store the number of nodes which should be displayed in the graph.
    private final int NUMBER_OF_NODES = 50;
    // Store the last time, when the sensor was called.
    private long lastDrawCallTimestamp;
    // Store last data for graphs.
    private ArrayList<float[]> gyroscopeNodes;
    private ArrayList<float[]> magnetometerNodes;
    private ArrayList<float[]> barometerNodes;
    private ArrayList<float[]> accelerometerNodes;

    private long totalFPS;
    private int count;

    // ProgressDialog and Toast
    private ProgressDialog dialog;
    private Toast toast;


    // Network variables
    private UDPConnection udpConnection;
    private String serverName;
    private int serverPort;
    private InetAddress serverAddr;
    private String localName;

    // For reading from port
    private Handler readHandler;
    private final int readFrequency = 5000;
    private Runnable readRunnable;

    // Timer for keepalive messages.
    private Handler keepAliveHandler;
    private final int keepAliveDelay = 15000; // 15 seconds.
    private Runnable keepAliveRunnable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        ViewPager pager = (ViewPager) findViewById(R.id.viewPager);
        pager.setAdapter(new MyPagerAdapter(getSupportFragmentManager()));

        // Create sensor manager.
        this.mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        // Instantiate sensors.
        this.mAccelerometer = this.mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        this.mGyroscope = this.mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        this.mMagnetometer = this.mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        this.mBarometer = this.mSensorManager.getDefaultSensor(Sensor.TYPE_PRESSURE);

        // Initialize lists.
        this.gyroscopeNodes = new ArrayList<>();
        this.magnetometerNodes = new ArrayList<>();
        this.barometerNodes = new ArrayList<>();
        this.accelerometerNodes = new ArrayList<>();

        // Initialize UDP Connection.
        this.udpConnection = new UDPConnection();

        // Create timer for keep alive messages.
        this.keepAliveHandler = new Handler();
        this.keepAliveRunnable = new Runnable() {
            @Override
            public void run() {
                new Keepalive().execute();
                keepAliveHandler.postDelayed(this, keepAliveDelay);
            }
        };

        this.readHandler = new Handler();
        this.readRunnable = new Runnable() {
            @Override
            public void run() {
                new BroadcastListen().execute();
                MainActivity.this.readHandler.postDelayed(this, readFrequency);
            }
        };

        // Listen to when the user changes the page of the pageViewer.
        pager.addOnPageChangeListener(new ViewPager.OnPageChangeListener() {
            @Override
            public void onPageScrolled(int position, float positionOffset,
                                       int positionOffsetPixels) {}

            @Override
            public void onPageSelected(int position) {
                onPageChanged(position);
            }

            @Override
            public void onPageScrollStateChanged(int state) {
                // Doesn't matter.
            }
        });

        this.totalFPS = 0;
        this.count = 0;
    }

    /**
     * OnClick Event: Register to server.
     *
     * @param v btnConnect
     */
    public void onClickConnect(View v) {
        EditText etServer = (EditText) findViewById(R.id.etServerAddress);
        EditText etPort = (EditText) findViewById(R.id.etPort);
        EditText etName = (EditText) findViewById(R.id.etName);

        this.serverName = etServer.getText().toString();
        this.serverPort = Integer.parseInt(etPort.getText().toString());
        this.localName = etName.getText().toString();

        // Displaying ProgressDialog and waiting for network operation
        this.dialog = new ProgressDialog(MainActivity.this);
        this.dialog.setMessage("Resolving server address...");
        this.dialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        this.dialog.setCancelable(false);
        this.dialog.show();

        // Perform network operation
        new ServerResolver().execute(this.serverName);

        // Start handler to call function every 15 seconds.
        this.keepAliveHandler.postDelayed(this.keepAliveRunnable, this.keepAliveDelay);
        this.readHandler.postDelayed(this.readRunnable, this.readFrequency);
    }

    /**
     * Asynchronous operation: resolving server address and send REGISTER signal.
     */
    private class ServerResolver extends AsyncTask<String, Void, Void> {
        @Override
        protected Void doInBackground(String... params) {
            try {
                System.getenv();
                MainActivity.this.serverAddr = InetAddress.getByName(params[0]);

                MainActivity.this.udpConnection.reg(MainActivity.this.serverAddr,
                        MainActivity.this.serverPort, MainActivity.this.localName);
            } catch (UnknownHostException e) {
                e.printStackTrace();
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            MainActivity.this.dialog.cancel();
            MainActivity.this.toast = Toast.makeText(MainActivity.this, "Connected",
                    Toast.LENGTH_SHORT);
            MainActivity.this.toast.show();
        }
    }

    /**
     * OnClock Event: Disconnect from server.
     *
     * @param v btnDisconnect
     */
    public void onClickDisconnect(View v) {
        // Displaying ProgressDialog and waiting for network operation
        this.dialog = new ProgressDialog(MainActivity.this);
        this.dialog.setMessage("Disconnecting...");
        this.dialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        this.dialog.setCancelable(false);
        this.dialog.show();

        // Unregistering
        new Unregistration().execute();
        this.keepAliveHandler.removeCallbacks(this.keepAliveRunnable);
        this.readHandler.removeCallbacks(this.readRunnable);
    }

    /**
     * Asynchronous operation: unregister from the server
     */
    private class Unregistration extends AsyncTask<Void, Void, Void> {
        @Override
        protected Void doInBackground(Void... params) {
            MainActivity.this.udpConnection.unReg();
            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            MainActivity.this.dialog.cancel();
            MainActivity.this.toast = Toast.makeText(MainActivity.this, "Disconnected",
                    Toast.LENGTH_SHORT);
            MainActivity.this.toast.show();
        }
    }


    /**
     * OnClick Event: Send Shake to server.
     *
     * @param v btnShake
     */
    public void onClickShake(View v) {
        // Sending event
        new ShakeEvent().execute();
        this.toast = Toast.makeText(MainActivity.this, "SHAKE SENT", Toast.LENGTH_SHORT);
        this.toast.show();
    }

    /**
     * Asynchronous operation: sending shake event
     */
    private class ShakeEvent extends AsyncTask<Void, Void, Void> {
        @Override
        protected Void doInBackground(Void... params) {
            MainActivity.this.udpConnection.shake();
            return null;
        }
    }

    /**
     * Asynchronous operation: sending keepalive request
     */
    private class Keepalive extends AsyncTask<Void, Void, Void> {
        @Override
        protected Void doInBackground(Void... params) {
            MainActivity.this.udpConnection.keepAlive();
            return null;
        }
    }

    /**
     * Asynchronous operation: listening to broadcasting
     */
    private class BroadcastListen extends AsyncTask<Void, Void, String> {
        @Override
        protected String doInBackground(Void... params) {
            return MainActivity.this.udpConnection.readBroadcast();
        }

        @Override
        protected void onPostExecute(String result) {
            if (null != result) {
                MainActivity.this.toast = Toast.makeText(MainActivity.this, result,
                        Toast.LENGTH_SHORT);
                MainActivity.this.toast.show();

                new BroadcastListen().execute();
            }
        }
    }

    /**
     * Resume sensors.
     */
    protected void onResume() {
        super.onResume();

        switch (this.currentPage) {

            case Accelerometer:
                this.mSensorManager.registerListener(this, this.mAccelerometer,
                        SensorManager.SENSOR_DELAY_UI);
                break;

            case Gyroscope:
                this.mSensorManager.registerListener(this, this.mGyroscope,
                        SensorManager.SENSOR_DELAY_UI);
                break;

            case Magnetometer:
                this.mSensorManager.registerListener(this, this.mMagnetometer,
                        SensorManager.SENSOR_DELAY_UI);
                break;

            case Barometer:
                this.mSensorManager.registerListener(this, this.mBarometer,
                        SensorManager.SENSOR_DELAY_UI);
                break;

            default:
                break;
        }
    }

    /**
     * Pause sensors.
     */
    protected void onPause() {
        super.onPause();

        this.mSensorManager.unregisterListener(this);
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        // Just continue if the last event is more than REFRESH_TIME_MS old.
        final int REFRESH_TIME_MS = 100;
        if (System.currentTimeMillis() - this.lastDrawCallTimestamp > REFRESH_TIME_MS) {
            this.lastDrawCallTimestamp = System.currentTimeMillis();
        } else {
            return;
        }

        switch (event.sensor.getType()) {

            case Sensor.TYPE_ACCELEROMETER:
                this.readAccelerometer(event.values);
                break;

            case Sensor.TYPE_GYROSCOPE:
                this.readGyroscope(event.values);
                break;

            case Sensor.TYPE_MAGNETIC_FIELD:
                this.readMagnetometer(event.values);
                break;

            case Sensor.TYPE_PRESSURE:
                this.readBarometer(event.values);
                break;

            default:
                break;
        }

    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        // Not needed up to now...
    }

    /**
     * Happens when a page of the pageViewer changes.
     *
     * @param position the position of the page in the pageViewer.
     */
    private void onPageChanged(int position) {
        // Check which page I am scrolling to.
        switch (position) {

            // Accelerometer page.
            case 0:
                this.currentPage = Page.Accelerometer;
                this.mSensorManager.unregisterListener(this);
                this.mSensorManager.registerListener(this, this.mAccelerometer,
                        SensorManager.SENSOR_DELAY_UI);
                this.totalFPS = 0;
                this.count = 0;
                break;

            // Gyroscope page.
            case 1:
                this.currentPage = Page.Gyroscope;
                this.mSensorManager.unregisterListener(this);
                this.mSensorManager.registerListener(this, this.mGyroscope,
                        SensorManager.SENSOR_DELAY_UI);
                this.totalFPS = 0;
                this.count = 0;
                break;

            // Magnetometer page.
            case 2:
                this.currentPage = Page.Magnetometer;
                this.mSensorManager.unregisterListener(this);
                this.mSensorManager.registerListener(this, this.mMagnetometer,
                        SensorManager.SENSOR_DELAY_UI);
                this.totalFPS = 0;
                this.count = 0;
                break;

            // Barometer page.
            case 3:
                this.currentPage = Page.Barometer;
                this.mSensorManager.unregisterListener(this);
                this.mSensorManager.registerListener(this, this.mBarometer,
                        SensorManager.SENSOR_DELAY_UI);
                this.totalFPS = 0;
                this.count = 0;
                break;

            // Never happens.
            default:
                break;
        }
    }

    /**
     * Return the fragment with the corresponding number out of the viewPage.
     *
     * @param itemNumber the number corresponding to a fragment
     * @return Fragment corresponding to the itemNumber
     */
    private Fragment getFragmentFromMyPageAdapter(int itemNumber) {
        ViewPager pager = (ViewPager) findViewById(R.id.viewPager);
        MyPagerAdapter myPagerAdapter = (MyPagerAdapter) pager.getAdapter();

        return myPagerAdapter.getItem(itemNumber);
    }

    /**
     * Read the values of the accelerometer.
     *
     * @param values contains values for x, y and z.
     */
    private void readAccelerometer(float[] values) {
        AccelerometerFragment af = (AccelerometerFragment) this.getFragmentFromMyPageAdapter(4);
        LinearLayout llAccelerometerCanvas
                = (LinearLayout) findViewById(R.id.llAccelerometerCanvas);

        // Add values to list.
        float[] v = this.calibrateAccelerometer(values);
        this.accelerometerNodes.add(new float[]{v[0], v[1], v[2]});
        // If there are too many values, remove the oldest.
        if (this.accelerometerNodes.size() > this.NUMBER_OF_NODES)
            this.accelerometerNodes.remove(0);

        // Send values to AccelerometerFragment.
        this.totalFPS = af.setSensorValues(this.accelerometerNodes, llAccelerometerCanvas,
                getApplicationContext().getResources(), this.totalFPS, this.count);
        this.count++;

        // Check if phone has been shaken.
        if (this.shaken(this.calibrateAccelerometer(values)))
            new ShakeEvent().execute();
    }

    /**
     * Calibrate the accelerometer.
     *
     * @param values values received from accelerometer.
     * @return calibrated values.
     */
    private float[] calibrateAccelerometer(float[] values) {
        if (this.calibrationReference == null) {
            this.calibrationReference = new float[3];
            this.calibrationReference[0] = values[0];
            this.calibrationReference[1] = values[1];
            this.calibrationReference[2] = values[2];

            return new float[] {0, 0, 0};
        } else {
            values[0] -= this.calibrationReference[0];
            values[1] -= this.calibrationReference[1];
            values[2] -= this.calibrationReference[2];

            return values;
        }
    }

    /**
     * Check if phone has been shaken.
     *
     * @param values Current sensor data from accelerometer.
     * @return true if phone has been shaken.
     */
    private Boolean shaken(float[] values) {
        // This works as follows:
        // If the phone gets driven in a specific direction and the drive is stronger than the
        // threshold, store the direction. If the phone gets driven in the opposite direction,
        // then shake happens!

        final float SHAKE_THRESHOLD = 4;
        if (values[0] > SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.xNeg
                || values[0] < -SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.xPos
                || values[1] > SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.yNeg
                || values[1] < -SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.yPos
                || values[2] > SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.zNeg
                || values[2] < -SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.zPos) {
            this.shakeDirection = ShakeDirection.zero;
            Toast.makeText(MainActivity.this, "SHAKE SENT", Toast.LENGTH_SHORT).show();
            return true;
        } else if (values[0] > SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.xPos;
            return false;
        } else if (values[0] < -SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.xNeg;
            return false;
        } else if (values[1] > SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.yPos;
            return false;
        } else if (values[1] < -SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.yNeg;
            return false;
        } else if (values[2] > SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.zPos;
            return false;
        } else if (values[2] < -SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.zNeg;
            return false;
        }

        return false;
    }

    /**
     * Read the values of the gyroscope.
     *
     * @param values values received from gyroscope.
     */
    private void readGyroscope(float[] values) {
        GyroscopeFragment gf = (GyroscopeFragment) this.getFragmentFromMyPageAdapter(1);
        LinearLayout llGyroscopeCanvas = (LinearLayout) findViewById(R.id.llGyroscopeCanvas);

        // Add values to list.
        this.gyroscopeNodes.add(new float[]{values[0], values[1], values[2]});
        // If there are too many values, remove the oldest.
        if (this.gyroscopeNodes.size() > this.NUMBER_OF_NODES)
            this.gyroscopeNodes.remove(0);

        // Send values to GyroscopeFragment.
        this.totalFPS = gf.setSensorValues(this.gyroscopeNodes, llGyroscopeCanvas,
                getApplicationContext().getResources(), this.totalFPS, this.count);
        this.count++;
    }


    /**
     * Read the values of the magnetometer.
     *
     * @param values values received from magnetometer.
     */
    private void readMagnetometer(float[] values) {
        MagnetometerFragment mf = (MagnetometerFragment) this.getFragmentFromMyPageAdapter(2);
        LinearLayout llMagnetometerCanvas = (LinearLayout) findViewById(R.id.llMagnetometerCanvas);

        // Add values to list.
        this.magnetometerNodes.add(new float[]{values[0], values[1], values[2]});
        // If there are too many values, remove the oldest.
        if (this.magnetometerNodes.size() > this.NUMBER_OF_NODES)
            this.magnetometerNodes.remove(0);

        // Send values to MagnetometerFragment.
        this.totalFPS = mf.setSensorValues(this.magnetometerNodes, llMagnetometerCanvas,
                getApplicationContext().getResources(), this.totalFPS, this.count);
        this.count++;
    }

    /**
     * Read the values from barometer.
     *
     * @param values values received from barometer.
     */
    private void readBarometer(float[] values) {
        BarometerFragment bf = (BarometerFragment) this.getFragmentFromMyPageAdapter(3);
        LinearLayout llBarometerCanvas = (LinearLayout) findViewById(R.id.llBarometerCanvas);

        // Add values to list.
        this.barometerNodes.add(new float[]{values[0], values[1], values[2]});
        // If there are too many values, remove the oldest.
        if (this.barometerNodes.size() > this.NUMBER_OF_NODES)
            this.barometerNodes.remove(0);

        // Send values to BarometerFragment.
        this.totalFPS = bf.setSensorValues(this.barometerNodes, llBarometerCanvas,
                getApplicationContext().getResources(), this.totalFPS, this.count);
        this.count++;
    }
}
