import React, { useState, useEffect, useRef } from "react";
import PageTitle from "../../components/utils/page-title/page-title";
import ProfileCreationFormFwd from "../../components/form/form-profile-creation/profile-creation-form";
import ProfileInterface from "../../interfaces/profile";
import ProjectInterface from "../../interfaces/project";
import styles from "../../styles/ProfileCreation.module.css";
import dynamic from "next/dynamic";

const initialProfile: ProfileInterface = {
  profileName: "",
  about: "",
  avatar: "",
  twitter: "",
  linkedin: "",
  indeed: "",
  github: "",
  reddit: "",
  stackoverflow: "",
  projects: [] as ProjectInterface[],
};

function ProfileCreation() {
  return (
    <div className={styles.procreWrapper}>
      <div className={styles.procreTitle}>
        <PageTitle title="Create Profile" />
      </div>
      <ProfileCreationFormFwd />
    </div>
  );
}
export default ProfileCreation;
