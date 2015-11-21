package com.example.michael.shake;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * Created by Michael on 20.11.2015.
 * Holds some functionality to create a UDP connection.
 */
class UDPConnection {

    // TYPE def.
    private final int TYPE_REGISTER = 1;
    private final int TYPE_UNREGISTER = 2;
    private final int TYPE_KEEPALIVE = 3;
    private final int TYPE_EVENT = 4;
    private final int TYPE_SHAKE = 5;

    // Server information
    private InetAddress serverAddr;
    private int serverPort;

    // Local information
    private String localName;
    private int localPort = 23333;
    private int localRecvPort = 23334;
    private boolean connection = false;

    // Data type and data
    private int TYPE_UNKN = 0;
    private int TYPE_REG = 1;
    private int TYPE_UNREG = 2;
    private int TYPE_KEP = 3;
    private int TYPE_EVE = 4;
    private int TYPE_SHK = 5;

    // Data
    private DatagramPacket REG, UNREG, KEP, EVE, SHK;
    private DatagramSocket sendSock;

    /**
     * Connect to the server with the given data.
     * @param serverAddr Server address
     * @param serverPort Port of server
     * @param localName Name of local
     */
    public void reg(InetAddress serverAddr, int serverPort, String localName) {
        // Initializing network variables
        // Server variables
        this.serverAddr = serverAddr;
        this.serverPort = serverPort;

        // Local variables
        this.localName = localName;


        // Setting up socket for sending and receiving data
        try {
            if (!this.connection) {
                this.sendSock = new DatagramSocket(this.localPort);
                this.sendSock.setSoTimeout(500);
            }
        }
        catch (IOException e) {
            e.printStackTrace();
        }

        // Initializing data
        this.initData();

        // Sending REGISTER signal
        try {
            this.sendSock.send(this.REG);
            this.connection = true;
        }
        catch (IOException e) {
            e.printStackTrace();
        }

    }

    /**
     * Disconnect from the server.
     */
    public void unReg() {
        if (this.connection) {
            try {
                this.sendSock.send(this.UNREG);
                this.connection = false;
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    /**
     *  Keep alive message which has to be send every 15s if connected with the server.
     */
    public void keepAlive() {
        if (this.connection) {
            try {
                this.sendSock.send(this.KEP);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * Send shake event if phone has been shaken.
     */
    public void shake() {
        if (this.connection) {
            try {
                // Event request
                byte [] rawEve = new byte[9];
                rawEve[0] = (byte)this.TYPE_EVE;

                ByteBuffer buf = ByteBuffer.allocate(8);
                buf.putLong(System.currentTimeMillis() / 1000L);
                buf.order(ByteOrder.BIG_ENDIAN);
                buf.position(0);
                buf.get(rawEve, 1, 8);

                this.EVE = new DatagramPacket(rawEve, 9);
                this.EVE.setAddress(this.serverAddr);
                this.EVE.setPort(this.serverPort);

                this.sendSock.send(this.EVE);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * Begin to read broadcasting.
     */
    public String readBroadcast() {
        if (!this.connection)
            return null;

        if (this.sendSock.isConnected())
            return null;


        byte [] buf = new byte[512];
        DatagramPacket incomingData = new DatagramPacket(buf, buf.length);
        try {
            this.sendSock.receive(incomingData);
        }
        catch (IOException e) {
            return null;
        }

        if (incomingData.getLength() < 10)
            return null;

        byte [] data = new byte[incomingData.getLength()];
        System.arraycopy(incomingData.getData(), 0, data, 0, incomingData.getLength());

        ByteBuffer wrapped = ByteBuffer.wrap(data, 1, 8);
        long ts = wrapped.getLong();
        Date tsDate = new Date(ts);
        DateFormat tsDateFormat = new SimpleDateFormat("MM/dd/yyyy HH:mm:ss");
        String tsString = tsDateFormat.format(tsDate);

        String name = new String(data, 10, incomingData.getLength() - 10);

        return name + " shaked at\n" + tsString;
    }


    /**
     * Initializing datagrams.
     */
    private void initData() {
        // Register request
        byte [] rawReg = new byte[2 + this.localName.length()];
        rawReg[0] = (byte)this.TYPE_REG;
        rawReg[1] = (byte)this.localName.length();
        System.arraycopy(this.localName.getBytes(), 0, rawReg, 2, this.localName.length());
        this.REG = new DatagramPacket(rawReg, 2 + this.localName.length());
        this.REG.setAddress(this.serverAddr);
        this.REG.setPort(this.serverPort);

        // Unregister request
        byte [] rawUnreg = new byte[1];
        rawUnreg[0] = (byte)this.TYPE_UNREG;
        this.UNREG = new DatagramPacket(rawUnreg, 1);
        this.UNREG.setAddress(this.serverAddr);
        this.UNREG.setPort(this.serverPort);

        // Keep alive request
        byte [] rawKep = new byte[1];
        rawKep[0] = (byte)this.TYPE_KEP;
        this.KEP = new DatagramPacket(rawKep, 1);
        this.KEP.setAddress(this.serverAddr);
        this.KEP.setPort(this.serverPort);
    }
}
