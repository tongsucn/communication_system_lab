package com.example.michael.powerplugswitch;

/**
 * Created by Michael on 02.12.2015.
 * Property class of a plug.
 */
class Plug {
    private String id;
    private String description;
    private Boolean state;

    public Plug() {
        this.id = "";
        this.description = "";
        this.state = false;
    }

    public Plug(String id, String description, Boolean state) {
        this.id = id;
        this.description = description;
        this.state = state;
    }

    public void setId(String id) {
        this.id = id;
    }

    public void setDescription(String description) {
        this.description = description;
    }

// --Commented out by Inspection START (06.12.2015 12:57):
//    public void setState(Boolean state) {
//        this.state = state;
//    }
// --Commented out by Inspection STOP (06.12.2015 12:57)

    public String getId() {
        return this.id;
    }

    public String getDescription() {
        return this.description;
    }

    public Boolean getState() {
        return this.state;
    }

    public String toString() {
        return this.id + ";" +  this.state.toString();
    }

    public void changeState() {
        this.state = !this.state;
    }
}
