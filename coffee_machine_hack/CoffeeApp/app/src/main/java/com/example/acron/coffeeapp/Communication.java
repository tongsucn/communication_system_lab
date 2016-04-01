package com.example.acron.coffeeapp;

import android.content.SharedPreferences;

import java.net.InetAddress;

/**
 * Created by acron on 11.02.2016.
 */
public class Communication {

    private static InetAddress serverAddress = null;
    private static SharedPreferences SP;

    private static boolean water = false;
    private static boolean beans = false;
    private static boolean tray = false;
    private static boolean cup = false;
    private static boolean machineStatus = false;

    private static boolean checkServerAddress(){
        InetAddress res = null;
        InetAddress localHost = null;
        try {
            res = InetAddress.getByName(SP.getString("serverIP", null));
            localHost = InetAddress.getLoopbackAddress();
        }catch (Exception e){
            e.printStackTrace();
            }
        if(res != null){
            serverAddress = res;
            return res != localHost;
        }else{
            return false;
        }
    }

    public static void setSharedPreferences(SharedPreferences sp){
        SP = sp;
    }

    /**
     *
     * @return current status of the machine (true - ON/ false - OFF)
     */
    public static boolean getMachineStatus(){
        return machineStatus;
    }

    /**
     *
     * @param status new status - true for ON, false for OFF
     * @return  new status of the machine (true - ON / false - OFF)
     */
    public static boolean setMachineStatus(boolean status){
        //TODO
        return true;
    }

    public static boolean getWaterTank(){
        return water;
    }

    public static boolean getTray(){
        return tray;
    }

    public static boolean getBeans(){
        return beans;
    }

    public static boolean getCup(){
        return cup;
    }

    public static String[] getProductList(){
        //TODO
        String[] res = {"Latte","Espresso","Cappuccino","Milk coffee", "Coffee","Steam"};
        return res;
    }

    public static String[] getStatistics(){
        //TODO
        return null;
    }

    public static boolean requestProduct(int prod){
        return checkServerAddress();
    }

    public static InetAddress getServerAddress(){
        return serverAddress;
    }
}
