package com.example.michi.myapplication;

import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.os.StrictMode;
import android.view.View;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Toast;

import org.xmlpull.v1.XmlPullParserException;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener {

    public static final String PREFS_NAME = "SharedPreferences";

    int mensaNumber = 0;
    String mensaTitle = "Academica";
    Boolean useEnglish = true;
    Boolean compressed = false;

    private int currentDay = 0;
    List<Weekday> weekdays = new ArrayList<>();
    HTTPRequest request = new HTTPRequest();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.setDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        // Initialize button to show the next day.
        final Button btnForward = (Button)findViewById(R.id.btnForward);
        btnForward.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                forward();
            }
        });

        // Initialize button to show the previous day.
        final Button btnBack = (Button)findViewById(R.id.btnBack);
        btnBack.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                backwards();
            }
        });

        // Otherwise you're not allowed to use internet in your app.
        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        // Restore prefereces.
        SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
        this.mensaNumber = settings.getInt("mensaNumber", 0);
        this.request.setActiveUrl(this.mensaNumber);
        this.mensaTitle = settings.getString("mensaTitle", "Academica");
        this.useEnglish = settings.getBoolean("useEnglish", true);
        this.compressed = settings.getBoolean("compressed", false);
        this.request.setCompressed(this.compressed);

        // Start.
        this.setTitle(this.mensaTitle);
        this.setLanguage(this.useEnglish);
        this.startHTTPRequest();
    }

    // Set the language of the returned food.
    // TRUE = english. FALSE = german.
    private void setLanguage(Boolean useEnglish) {
        this.useEnglish = useEnglish;
        this.request.setLanguage(this.useEnglish);
        this.startHTTPRequest();
    }

    // Set the mensa of the returned food.
    private void setMensa(int mensaNumber, String mensaTitle) {
        this.mensaNumber = mensaNumber;
        this.mensaTitle = mensaTitle;

        this.setTitle(this.mensaTitle);
        this.request.setActiveUrl(this.mensaNumber);

        this.startHTTPRequest();
    }

    // Show the previous day.
    private void backwards() {
        if (this.weekdays.size() == 0) {
            this.currentDay = 0;
        }
        else {
            this.currentDay--;

            if (this.currentDay < 0)
                this.currentDay = this.weekdays.size() - 1;

            this.drawTable();
        }
    }

    // Show the next day.
    private void forward() {
        if (this.weekdays.size() == 0) {
            this.currentDay = 0;
        }
        else {
            this.currentDay++;

            if (this.currentDay > this.weekdays.size() - 1)
                this.currentDay = 0;

            this.drawTable();
        }
    }

    // Receive HTTP source code from website.
    private void startHTTPRequest() {
        this.weekdays = new ArrayList<>();

        try {
            this.weekdays = request.parse();
            this.drawTable();
        }
        catch (XmlPullParserException e) {
            e.printStackTrace();

            // Show toast.
            Toast toast = Toast.makeText(getApplicationContext(),
                    "Server could not be found.", Toast.LENGTH_LONG);
            toast.show();

            this.drawTable(); // Just remove the last table.
        }
    }


    // Draw table to show the food.
    private void drawTable() {
        TableLayout tblFood = (TableLayout)findViewById(R.id.tblFood);
        tblFood.removeAllViews();

        // Do nothing if we have no data.
        if (this.weekdays.size() == 0)
            return;

        // Prepare table.
        tblFood.setStretchAllColumns(true);
        tblFood.bringToFront();

        // Add date to textView.
        TextView tvDate = (TextView)findViewById(R.id.tvDate);
        tvDate.setText(this.weekdays.get(this.currentDay).getDate());

        // If a note is available, show it.
        if (!this.weekdays.get(this.currentDay).getNote().equalsIgnoreCase("")) {
            TableRow trNote = new TableRow(this);
            TextView tvNote = new TextView(this);
            tvNote.setText(this.weekdays.get(this.currentDay).getNote());
            trNote.addView(tvNote);
            TableRow.LayoutParams params2 = (TableRow.LayoutParams)tvNote.getLayoutParams();
            params2.span = 2;
            tvNote.setLayoutParams(params2);
            tblFood.addView(trNote);

            return; // Don't draw the table below if a note is available.
        }

        // Add data to table.
        for (int i = 0; i < this.weekdays.get(this.currentDay).getDishes().size(); i++) {
            TableRow tr = new TableRow(this);
            tr.setBackgroundColor(Color.argb(125, 142, 186, 229));

            TextView tvCategory = new TextView(this);
            tvCategory.setText(this.weekdays.get(this.currentDay).getDishes().get(i).getCategory());
            tvCategory.setTypeface(null, Typeface.BOLD);
            tr.addView(tvCategory);

            TextView tvPrice = new TextView(this);
            tvPrice.setText(this.weekdays.get(this.currentDay).getDishes().get(i).getPrice());
            tvPrice.setTypeface(null, Typeface.BOLD);
            tvPrice.setTextAlignment(View.TEXT_ALIGNMENT_TEXT_END);
            tr.addView(tvPrice);

            tblFood.addView(tr);

            TableRow tr2 = new TableRow(this);
            tr2.setBackgroundColor(Color.argb(255, 142, 186, 229));

            TextView tvExtraMenue = new TextView(this);
            tvExtraMenue.setText(this.weekdays.get(this.currentDay).getDishes().get(i).getMenue());
            tvExtraMenue.append(this.weekdays.get(this.currentDay).getDishes().get(i).getExtra());
            tvExtraMenue.setWidth(tblFood.getWidth());
            tr2.addView(tvExtraMenue);
            TableRow.LayoutParams params2 = (TableRow.LayoutParams)tvExtraMenue.getLayoutParams();
            params2.span = 2;
            tvExtraMenue.setLayoutParams(params2);

            tblFood.addView(tr2);
        }
    }

    @Override
    public void onBackPressed() {
        // Store preferences.
        SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
        SharedPreferences.Editor editor = settings.edit();
        editor.putInt("mensaNumber", this.mensaNumber);
        editor.putString("mensaTitle", this.mensaTitle);
        editor.putBoolean("useEnglish", this.useEnglish);
        editor.putBoolean("compressed", this.compressed);
        //editor.commit();
        editor.apply();

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        switch (item.getItemId()) {
            case R.id.action_english:
                this.setLanguage(true);
                break;
            case R.id.action_german:
                this.setLanguage(false);
                break;
            case R.id.action_compressed:
                this.compressed = true;
                this.request.setCompressed(true);
                this.startHTTPRequest();
                break;
            case R.id.action_uncompressed:
                this.compressed = false;
                this.request.setCompressed(false);
                this.startHTTPRequest();
                break;
            default:
                break;
        }
        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.action_mensa_academica:
                this.setMensa(0, "Academica");
                break;
            case R.id.action_mensa_ahornstrasse:
                this.setMensa(1, "Ahornstraße");
                break;
            case R.id.action_mensa_templergraben:
                this.setMensa(2, "Bistro Templergraben");
                break;
            case R.id.action_mensa_bayernallee:
                this.setMensa(3, "Bayernallee");
                break;
            case R.id.action_mensa_eupener:
                this.setMensa(4, "Eupener Straße");
                break;
            case R.id.action_mensa_goethestrasse:
                this.setMensa(5, "Goethestraße");
                break;
            case R.id.action_mensa_vita:
                this.setMensa(6, "Mensa Vita");
                break;
            case R.id.action_mensa_cafete:
                this.setMensa(7, "Forum Cafete");
                break;
            case R.id.action_mensa_juelich:
                this.setMensa(8, "Mensa Jülich");
                break;
            default:
                break;
        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }
}
