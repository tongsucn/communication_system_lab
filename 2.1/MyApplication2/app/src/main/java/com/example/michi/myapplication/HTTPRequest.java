package com.example.michi.myapplication;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;
import org.xmlpull.v1.XmlPullParserFactory;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.util.List;
import java.util.ArrayList;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;

import java.net.Proxy;
import java.net.InetSocketAddress;
import java.net.HttpURLConnection;
import java.util.Scanner;

/**
 * Created by michael deutschen, tong su on 29.10.2015.
 * Send HTTPRequest to specified website and parse it into List<Weekday> format.
 */
class HTTPRequest {

    // URLs whose content we want to parse. Only add the german url's, because the english one's are derived from them.
    private int activeUrl;
    private final String[] urls = {"http://www.studentenwerk-aachen.de/speiseplaene/academica-w.html",
                            "http://www.studentenwerk-aachen.de/speiseplaene/ahornstrasse-w.html",
                            "http://www.studentenwerk-aachen.de/speiseplaene/templergraben-w.html",
                            "http://www.studentenwerk-aachen.de/speiseplaene/bayernallee-w.html",
                            "http://www.studentenwerk-aachen.de/speiseplaene/eupenerstrasse-w.html",
                            "http://www.studentenwerk-aachen.de/speiseplaene/goethestrasse-w.html",
                            "http://www.studentenwerk-aachen.de/speiseplaene/vita-w.html",
                            "http://www.studentenwerk-aachen.de/speiseplaene/forum-w.html",
                            "http://www.studentenwerk-aachen.de/speiseplaene/juelich-w.html"};

    // Decide which language should be parsed. True = english. False = german.
    private Boolean englishLanguage;

    // Decide if compression should be used. If true, a proxy is used.
    private Boolean compressed;

    // List of (usually 10) weekdays, which itself contain the dishes of the day.
    private List<Weekday> weekdays;

    // Variables needed for parsing.
    private Weekday weekday;
    private Dish dish;
    private String whatsNext;   // Defines what the parser expects as the next text (category, menu, price or extra).
    private String lastText;    // Ugly variable that stores the last read text. Needed to catch the date.

    // Constructor.
    public HTTPRequest() {
        this.activeUrl = 0;
        this.englishLanguage = true;
        this.compressed =  false;
        this.weekdays = new ArrayList<>();
        this.weekday = new Weekday();
        this.dish = new Dish();
        this.whatsNext = "";
        this.lastText = "";
    }

    // Receive InputStream from Website.
    private InputStream getInputStream() {
        try {
            URLConnection connection = new URL(this.getUrl()).openConnection();
            return connection.getInputStream();
        }
        catch (IOException e) {
            e.printStackTrace();
        }

        // Return empty stream if above fails.
        return new ByteArrayInputStream("".getBytes(StandardCharsets.UTF_8));
    }

    // Receive InputStream from Website and convert InputStream to String.
    private String convertInputStreamToString() throws IOException {
        InputStream inputStream = this.getInputStream();

        BufferedReader r = new BufferedReader(new InputStreamReader(inputStream));
        StringBuilder total = new StringBuilder();
        String line;
        while ((line = r.readLine()) != null) {
            total.append(line);
        }
        return total.toString();
    }

    // Connecting to proxy server and getting compressed stream
    private InputStream getCompressedInputStream() {
        // Connecting to proxy server
        try {
            Proxy compressProxy = new Proxy(Proxy.Type.HTTP,
                    new InetSocketAddress("cslectures.tongsucn.com", 8123));
            URL url = new URL(this.getUrl());
            HttpURLConnection conn
                = (HttpURLConnection) url.openConnection(compressProxy);
            return conn.getInputStream();
        }
        catch (IOException e) {
            e.printStackTrace();
        }

        // Return empty byte input stream if failed.
        return new ByteArrayInputStream("".getBytes(StandardCharsets.UTF_8));
    }

    // Receiving compressed InputStream from proxy and convert it into String
    private String convertCompressedInputStreamToString() {
        // Getting compressed stream
        InputStream inStream = getCompressedInputStream();

        return new Scanner(inStream, "UTF-8").useDelimiter("\\A").next();
    }

    // Parse website.
    public List<Weekday> parse() throws XmlPullParserException {
        // Init.
        XmlPullParserFactory factory;
        XmlPullParser parser;
        String inputStreamString;
        this.weekdays = new ArrayList<>();
        this.dish = new Dish();
        this.weekday = new Weekday();

        try {
            factory = XmlPullParserFactory.newInstance();
            factory.setNamespaceAware(true);
            parser = factory.newPullParser();

            // Convert InputStream -> String -> Replace & in String -> InputStream.
            if (this.compressed)
                inputStreamString = this.convertCompressedInputStreamToString();
            else
                inputStreamString = this.convertInputStreamToString();

            inputStreamString = inputStreamString.replaceAll("&", "&amp;");

            // Cut out all content between " <sup> ... </sup>".
            inputStreamString = inputStreamString.replaceAll(" <sup>.*?</sup>", "");

            // Give stream to parser.
            parser.setInput(new ByteArrayInputStream(inputStreamString.getBytes(StandardCharsets.UTF_8)), null);

            int eventType = parser.getEventType();

            // Repeat until the document ends.
            while (eventType != XmlPullParser.END_DOCUMENT) {
                switch (eventType) {

                    case XmlPullParser.START_TAG:
                        this.parseStartTag(parser);
                        break;

                    case XmlPullParser.TEXT :
                        this.parseText(parser);
                        break;

                    case XmlPullParser.END_TAG:
                        break;

                    default:
                        break;
                }

                eventType = parser.next();
            }

            // After reading the whole document, the two objects must be added to weekdays (if they are edited).
            if (!this.dish.getCategory().equalsIgnoreCase(""))
                this.weekday.addDish(this.dish);
            this.weekdays.add(this.weekday);
        }
        catch (IOException e) {
            e.printStackTrace();
        }

        return this.weekdays;
    }

    // Parse the content, if parser already detected a XmlPullParser.START_TAG.
    // Submethod of this.parse().
    private void parseStartTag(XmlPullParser parser) {
        if (parser.getAttributeCount() > 0) {
            switch(parser.getAttributeName(0)) {

                case "id":
                    String str = parser.getAttributeValue(0);

                    if (this.isWeekday(str)) {
                        // If the current weekday is not new, save it.
                        if (!this.weekday.getDay().contentEquals("")) {
                            this.weekday.addDish(this.dish);
                            this.dish = new Dish();
                            this.weekdays.add(this.weekday);
                        }
                        // Create new weekday and set day and date.
                        this.weekday = new Weekday();
                        this.weekday.setDay(str);
                        this.weekday.setDate(this.lastText);
                    }
                    else if (str.equalsIgnoreCase("note")) {
                        //this.weekday.setNote(str);
                        this.whatsNext = "note";
                    }
                    break;

                case "class":
                    // Just look up what comes in the next text.
                    switch (parser.getAttributeValue(0)) {
                        case "category":
                            this.whatsNext = "category";
                            break;
                        case "menue":
                            this.whatsNext = "menue";
                            break;
                        case "price":
                            this.whatsNext = "price";
                            break;
                        case "extra":
                            this.whatsNext = "extra";
                            break;
                        default:
                            break;
                    }
                    break;

                default:
                    break;
            }
        }
    }

    // Parse the content, if parser already detected a XmlPullParser.TEXT.
    // Submethod of this.parse().
    private void parseText(XmlPullParser parser) {
        String str = this.format(parser.getText());

        if (!(str.isEmpty() || str.contentEquals(""))) {
            switch (this.whatsNext) {

                case "category":
                    // If the current dish is not new, save it.
                    if (!this.dish.getCategory().contentEquals(""))
                        this.weekday.addDish(this.dish);
                    // Create new dish and set category.
                    this.dish = new Dish();
                    this.dish.setCategory(str);
                    this.whatsNext = "";
                    break;

                case "menue":
                    this.dish.setMenue(str);
                    this.whatsNext = "";
                    break;

                case "price":
                    this.dish.setPrice(str);
                    this.whatsNext = "";
                    break;

                case "extra":
                    this.dish.setExtra(str);
                    this.whatsNext = "";
                    break;

                case "note":
                    this.weekday.setNote(str);
                    this.whatsNext = "";
                    break;

                default:
                    // Must be saved for the next loop, because the id="weekday" comes next.
                    this.lastText = str;
                    break;
            }
        }
    }

    // Replace annoying characters.
    private String format(String s) {
        s = s.replaceAll("\n", "");
        s = s.replaceAll("\t", "");
        s = s.trim();
        return s;
    }

    // Check if the given String equals a weekday.
    private Boolean isWeekday(String str) {
        return (str.equalsIgnoreCase("montag")
                || str.equalsIgnoreCase("dienstag")
                || str.equalsIgnoreCase("mittwoch")
                || str.equalsIgnoreCase("donnerstag")
                || str.equalsIgnoreCase("freitag")
                || str.equalsIgnoreCase("montagNaechste")
                || str.equalsIgnoreCase("dienstagNaechste")
                || str.equalsIgnoreCase("mittwochNaechste")
                || str.equalsIgnoreCase("donnerstagNaechste")
                || str.equalsIgnoreCase("freitagNaechste"));
    }

    // Set the active URL. Used to change the mensa.
    public void setActiveUrl(int activeUrl) {
        if (activeUrl > this.urls.length - 1 || activeUrl < 0)
            this.activeUrl = 0;
        else
            this.activeUrl = activeUrl;
    }

    /*
    public int getActiveUrl() {
        return this.activeUrl;
    }
    */

    // Set the language. True = english. False = german.
    public void setLanguage(Boolean englishLanguage) {
        this.englishLanguage = englishLanguage;
    }

    /*
    // Get the language. True = english. False = german.
    public Boolean getLanguage() {
        return this.englishLanguage;
    }
    */

    // Get the current url in the correct language.
    private String getUrl() {
        String str = this.urls[this.activeUrl];

        // If english, edit the url.
        if (this.englishLanguage)
            str = str.replace(".html", "-en.html");

        return str;
    }

    // Set if compression should be used.
    public void setCompressed(Boolean compressed) {
        this.compressed = compressed;
    }

    /*
    // Get if compression is used.
    public Boolean getCompressed() {
        return this.compressed;
    }
    */
}
