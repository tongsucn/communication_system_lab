package com.example.acron.coffeeapp;

import android.app.ActionBar;
import android.graphics.Typeface;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.GridLayout;
import android.widget.ImageView;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener {

    public String defaultMachine = "Coffee Machine 1";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new CustomViewListener());

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.setDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        fillContent();
    }

    @Override
    public void onBackPressed() {
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
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.nav_coffeecontrols) {
            // Handle the camera action
        } else if (id == R.id.nav_statistics) {

        } else if (id == R.id.nav_manage) {

        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    public void fillContent(){





        TextView txtCup = (TextView) findViewById(R.id.txtCup);
        ImageView imgCup = (ImageView) findViewById(R.id.imgCup);
        ImageView imgCupAv = (ImageView) findViewById(R.id.imgCupStatus);
        TextView txtWater = (TextView) findViewById(R.id.txtWater);
        ImageView imgWater = (ImageView) findViewById(R.id.imgWater);
        ImageView imgWaterAv = (ImageView) findViewById(R.id.imgWaterStatus);
        TextView txtTray = (TextView) findViewById(R.id.txtTray);
        ImageView imgTray = (ImageView) findViewById(R.id.imgTray);
        ImageView imgTrayAv = (ImageView) findViewById(R.id.imgTrayStatus);


        txtCup.setText("Cup detection: ");
        imgCup.setBackgroundResource(R.mipmap.ic_cup);
        imgCupAv.setBackgroundResource(Communication.getCup() ? R.mipmap.ic_cm : R.mipmap.ic_x);



        txtWater.setText("Water tank status: ");
        imgWater.setBackgroundResource(R.mipmap.ic_water);
        imgWaterAv.setBackgroundResource(Communication.getWaterTank() ? R.mipmap.ic_cm : R.mipmap.ic_x);


        txtTray.setText("Drip tray status: ");
        imgTray.setBackgroundResource(R.mipmap.ic_tray);
        imgTrayAv.setBackgroundResource(Communication.getWaterTank() ? R.mipmap.ic_cm : R.mipmap.ic_x);



    }
}
