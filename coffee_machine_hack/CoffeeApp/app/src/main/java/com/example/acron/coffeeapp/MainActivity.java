package com.example.acron.coffeeapp;


import android.content.Intent;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.design.widget.FloatingActionButton;

import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.ToggleButton;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener {

    public String defaultMachine = "Coffee Machine 1";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        SharedPreferences SP = PreferenceManager.getDefaultSharedPreferences(this);
        Communication.setSharedPreferences(SP);
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
        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.nav_coffeecontrols) {
            updateContent();
        } else if (id == R.id.nav_statistics) {

        } else if (id == R.id.nav_manage) {
            startActivity(new Intent(this, SettingActivity.class));
            return true;
        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    public void fillContent(){
        TextView txtPower = (TextView) findViewById(R.id.txtPower);
        ImageView imgPower = (ImageView)findViewById(R.id.imgPower);
        TextView txtCup = (TextView) findViewById(R.id.txtCup);
        ImageView imgCup = (ImageView) findViewById(R.id.imgCup);
        TextView txtBeans = (TextView) findViewById(R.id.txtBeans);
        ImageView imgBeans = (ImageView) findViewById(R.id.imgBeans);
        TextView txtWater = (TextView) findViewById(R.id.txtWater);
        ImageView imgWater = (ImageView) findViewById(R.id.imgWater);
        TextView txtTray = (TextView) findViewById(R.id.txtTray);
        ImageView imgTray = (ImageView) findViewById(R.id.imgTray);

        txtPower.setText("Machine status: ");
        imgPower.setBackgroundResource(R.mipmap.ic_power);
        txtCup.setText("Cup detection: ");
        imgCup.setBackgroundResource(R.mipmap.ic_cup);
        txtBeans.setText("Bean status: ");
        imgBeans.setBackgroundResource(R.mipmap.ic_beans);
        txtWater.setText("Water tank status: ");
        imgWater.setBackgroundResource(R.mipmap.ic_water);
        txtTray.setText("Drip tray status: ");
        imgTray.setBackgroundResource(R.mipmap.ic_tray);

        String[] products = Communication.getProductList();
        ToggleButton tB;
        switch(products.length){
            case 6:{
                tB = (ToggleButton) findViewById(R.id.btnProd6);
                tB.setText(products[5]);
                tB.setTextOff(products[5]);
                tB.setTextOn(products[5]);
                tB.setVisibility(View.VISIBLE);
            }
            case 5:{
                tB = (ToggleButton) findViewById(R.id.btnProd5);
                tB.setText(products[4]);
                tB.setTextOff(products[4]);
                tB.setTextOn(products[4]);
                tB.setVisibility(View.VISIBLE);
            }
            case 4:{
                tB = (ToggleButton) findViewById(R.id.btnProd4);
                tB.setText(products[3]);
                tB.setTextOff(products[3]);
                tB.setTextOn(products[3]);
                tB.setVisibility(View.VISIBLE);
            }
            case 3:{
                tB = (ToggleButton) findViewById(R.id.btnProd3);
                tB.setText(products[2]);
                tB.setTextOff(products[2]);
                tB.setTextOn(products[2]);
                tB.setVisibility(View.VISIBLE);
            }
            case 2:{
                tB = (ToggleButton) findViewById(R.id.btnProd2);
                tB.setText(products[1]);
                tB.setTextOff(products[1]);
                tB.setTextOn(products[1]);
                tB.setVisibility(View.VISIBLE);
            }
            case 1:{
                tB = (ToggleButton) findViewById(R.id.btnProd1);
                tB.setText(products[0]);
                tB.setTextOff(products[0]);
                tB.setTextOn(products[0]);
                tB.setVisibility(View.VISIBLE);
                break;
            }
            default:{

            }
        }

        ProductButtonListener tbl = new ProductButtonListener();
        ToggleButton btnProd1 = (ToggleButton) findViewById(R.id.btnProd1);
        btnProd1.setOnClickListener(tbl);
        ToggleButton btnProd2 = (ToggleButton) findViewById(R.id.btnProd2);
        btnProd2.setOnClickListener(tbl);
        ToggleButton btnProd3 = (ToggleButton) findViewById(R.id.btnProd3);
        btnProd3.setOnClickListener(tbl);
        ToggleButton btnProd4 = (ToggleButton) findViewById(R.id.btnProd4);
        btnProd4.setOnClickListener(tbl);
        ToggleButton btnProd5 = (ToggleButton) findViewById(R.id.btnProd5);
        btnProd5.setOnClickListener(tbl);
        ToggleButton btnProd6 = (ToggleButton) findViewById(R.id.btnProd6);
        btnProd6.setOnClickListener(tbl);

        updateContent();
    }

    public void updateContent(){

        ImageView imgPowerAv = (ImageView) findViewById(R.id.imgPowerStatus);
        ImageView imgCupAv = (ImageView) findViewById(R.id.imgCupStatus);
        ImageView imgBeansAv = (ImageView) findViewById(R.id.imgBeanStatus);
        ImageView imgWaterAv = (ImageView) findViewById(R.id.imgWaterStatus);
        ImageView imgTrayAv = (ImageView) findViewById(R.id.imgTrayStatus);

        imgPowerAv.setBackgroundResource(Communication.getMachineStatus() ? R.mipmap.ic_cm : R.mipmap.ic_x);
        imgCupAv.setBackgroundResource(Communication.getCup() ? R.mipmap.ic_cm : R.mipmap.ic_x);
        imgBeansAv.setBackgroundResource(Communication.getBeans() ? R.mipmap.ic_cm : R.mipmap.ic_x);
        imgWaterAv.setBackgroundResource(Communication.getWaterTank() ? R.mipmap.ic_cm : R.mipmap.ic_x);
        imgTrayAv.setBackgroundResource(Communication.getTray() ? R.mipmap.ic_cm : R.mipmap.ic_x);
    }
}
